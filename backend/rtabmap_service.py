"""
RTAB-Map Service Module

This module contains the RTABMapService class and related utilities for:
- Managing RTAB-Map database operations
- Processing images for localization
- Parsing localization output
- Coordinate transformations and utility functions
"""

import re
import time
import math
import json
import logging
import asyncio
import shutil
import sqlite3
import struct
from typing import Optional, List, Dict
from pathlib import Path

# Set up logging
logger = logging.getLogger("rtabmap")

# Define base data directory
DATA_DIR = Path("/data")


# --- Utility Functions ---

def quaternion_to_rpy(qx, qy, qz, qw):
    """
    Convert a quaternion into Euler angles (roll, pitch, yaw).
    Returns angles in radians.
    """
    # roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # pitch (y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)

    # yaw (z-axis rotation)
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


def rotation_matrix_to_quaternion(r11, r12, r13, r21, r22, r23, r31, r32, r33):
    """
    Convert a 3x3 rotation matrix to a quaternion (qx, qy, qz, qw).
    """
    tr = r11 + r22 + r33
    if tr > 0:
        S = math.sqrt(tr + 1.0) * 2
        qw = 0.25 * S
        qx = (r32 - r23) / S
        qy = (r13 - r31) / S
        qz = (r21 - r12) / S
    elif (r11 > r22) and (r11 > r33):
        S = math.sqrt(1.0 + r11 - r22 - r33) * 2
        qw = (r32 - r23) / S
        qx = 0.25 * S
        qy = (r12 + r21) / S
        qz = (r13 + r31) / S
    elif r22 > r33:
        S = math.sqrt(1.0 + r22 - r11 - r33) * 2
        qw = (r13 - r31) / S
        qx = (r12 + r21) / S
        qy = 0.25 * S
        qz = (r23 + r32) / S
    else:
        S = math.sqrt(1.0 + r33 - r11 - r22) * 2
        qw = (r21 - r12) / S
        qx = (r13 + r31) / S
        qy = (r23 + r32) / S
        qz = 0.25 * S
    return qx, qy, qz, qw


def get_frame_global_coordinates(cursor, frame_id: int) -> Optional[Dict]:
    """
    Get GLOBAL coordinates for a frame from database metadata.
    
    IMPORTANT: Returns global coordinates from RTAB-Map's optimized pose graph,
    NOT relative coordinates from the Node table.
    
    Args:
        cursor: Database cursor
        frame_id: Frame/node ID to query
    
    Returns:
        dict with keys: x, y, z, roll, pitch, yaw (global coordinates in meters)
        None if frame not found or no metadata
    
    Example:
        pose = get_frame_global_coordinates(cursor, 397)
        # Returns: {'x': 7.086, 'y': -36.280, 'z': 0.163, ...}
    """
    try:
        cursor.execute("SELECT metadata_json FROM ObjMeta WHERE frame_id = ?", (frame_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            logger.warning(f"No metadata found for frame {frame_id}")
            return None
        
        metadata = json.loads(result[0])
        
        # Handle dict structure (new format with global_pose)
        if isinstance(metadata, dict) and 'global_pose' in metadata:
            pose = metadata['global_pose']
            
            return {
                'x': float(pose['x']),
                'y': float(pose['y']),
                'z': float(pose['z']),
                'roll': float(pose['roll']),
                'pitch': float(pose['pitch']),
                'yaw': float(pose['yaw'])
            }
        
        logger.warning(f"No global_pose in metadata for frame {frame_id}")
        return None
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"Error parsing global coordinates for frame {frame_id}: {e}")
        return None


def parse_localization_output(output: str) -> Optional[Dict]:
    """
    Parse the output from rtabmap-console to extract localization pose and related info.
    Returns a dictionary with pose data and IDs, or None if parsing fails.
    """
    logger.info("=== parse_localization_output function called! ===")
    
    # Remove ANSI escape sequences for clean parsing
    ansi_escape = re.compile(r'\x1B\[[0-9;]*[A-Za-z]')
    cleaned_output = ansi_escape.sub('', output)
    logger.info(f"FULL Cleaned RTAB-Map output:\n{cleaned_output}")

    # Look for ALL iteration lines to see all hypothesis matches
    all_matches = []
    pic_id = None
    hypothesis_value = None
    
    # Pattern: iteration(1) loop(95) hyp(0.03) time=0.104099s/0.104109s *
    # Use DOTALL and MULTILINE flags to handle newlines between elements
    logger.info(f"Cleaned output contains 'iteration(' : {'iteration(' in cleaned_output}")
    if 'iteration(' in cleaned_output:
        logger.info("Iteration line should be found, checking regex...")
        for line in cleaned_output.split('\n'):
            if 'iteration(' in line:
                logger.info(f"Iteration line found: {repr(line.strip())}")
    
    # Use multi-line regex with non-greedy matching to handle newlines
    # Pattern captures: loop_id, hypothesis - Updated for new format with "high()" instead of "loop()"
    pattern = r"iteration\(\d+\).*?(?:loop|high)\((\d+)\).*?hyp\(([\d.]+)\)"
    iteration_matches = re.findall(pattern, cleaned_output, re.DOTALL | re.MULTILINE)
    
    # Debug: check if the string contains "iteration(" at all
    if "iteration(" in cleaned_output:
        logger.info("Found 'iteration(' in output - regex should work")
        # Find the exact line
        for line in cleaned_output.split('\n'):
            if 'iteration(' in line:
                logger.info(f"Iteration line found: {repr(line.strip())}")
    else:
        logger.info("NO 'iteration(' found in cleaned output!")
    
    if iteration_matches:
        logger.info(f"Found {len(iteration_matches)} iteration matches:")
        for i, (match_pic_id, match_hyp) in enumerate(iteration_matches):
            match_pic_id = int(match_pic_id)
            match_hyp = float(match_hyp)
            logger.info(f"  Match {i+1}: pic_id={match_pic_id}, hypothesis={match_hyp}")
            all_matches.append((match_pic_id, match_hyp))
            
            # Check if this specific match is node 95
            if match_pic_id == 95:
                logger.info(f"FOUND NODE 95! hypothesis={match_hyp}")
        
        # Use the first (highest) match for final result
        pic_id, hypothesis_value = iteration_matches[0]
        pic_id = int(pic_id)
        hypothesis_value = float(hypothesis_value)
        
        # Check if hypothesis meets threshold - VERY LOW threshold for camera images 
        if hypothesis_value >= 0.005:  # LOWERED from 0.01 - Accept very weak matches for camera images
            logger.debug(f"Found valid hypothesis: pic_id={pic_id}, hypothesis={hypothesis_value}")
            has_valid_match = True
        else:
            logger.debug(f"Hypothesis below threshold (0.005): pic_id={pic_id}, hypothesis={hypothesis_value}")
            has_valid_match = False
    else:
        logger.debug("No iteration line found with primary pattern, trying fallback patterns")
        
        # Try more flexible patterns as fallback
        loop_pattern = r"loop\((\d+)\)"
        loop_matches = re.findall(loop_pattern, cleaned_output)
        
        # More flexible hypothesis pattern to catch "hypothesis=X.XX" format too
        hyp_pattern = r"(?:hyp\(([\d.]+)\)|hypothesis[=\s]+([\d.]+))"
        hyp_matches_raw = re.findall(hyp_pattern, cleaned_output)
        # Flatten the tuple results and filter out empty strings
        hyp_matches = [match for group in hyp_matches_raw for match in group if match]
        
        logger.info(f"[DEBUG] Fallback loop matches: {loop_matches}")
        logger.info(f"[DEBUG] Fallback hyp matches: {hyp_matches}")
        
        if loop_matches and hyp_matches:
            # Use the first matches
            pic_id = int(loop_matches[0])
            hypothesis_value = float(hyp_matches[0])
            all_matches.append((pic_id, hypothesis_value))
            
            logger.info(f"[DEBUG] Fallback match found: pic_id={pic_id}, hypothesis={hypothesis_value}")
            
            if hypothesis_value >= 0.005:  # LOWERED from 0.01
                logger.debug(f"Found valid fallback hypothesis: pic_id={pic_id}, hypothesis={hypothesis_value}")
                has_valid_match = True
            else:
                logger.debug(f"Fallback hypothesis below threshold (0.005): pic_id={pic_id}, hypothesis={hypothesis_value}")
                has_valid_match = False
        else:
            logger.debug("No matches found even with fallback patterns")
            has_valid_match = False

    # If we have a valid match, we need to return the pose for that pic_id
    # Since we don't have the actual localization pose in the output, we'll need to 
    # return the pic_id and let the calling code handle getting the pose from the database
    if has_valid_match and pic_id is not None:
        return {
            "pic_id": pic_id,
            "hypothesis_value": hypothesis_value,
            "localization_successful": True,
            "all_matches": all_matches  # Include all matches for debugging
        }
    
    # If no valid match found, return a failed localization
    return {
        "localization_successful": False,
        "map_id": None,
        "all_matches": all_matches  # Include all matches for debugging
    }


class RTABMapService:
    """
    A persistent RTAB-Map service that keeps the database loaded in memory.
    Uses a long-running RTABMap process and communicates with it via temporary files.
    """
    
    def __init__(self):
        self.db_path: Optional[Path] = None
        self.is_initialized = False
        self.lock = asyncio.Lock()
        self.image_counter = 0
        self.base_rtabmap_params: List[str] = [] # Base parameters for rtabmap-console

    def _parse_and_format_pose(self, node_id, pose_data, precision=5):
        """Helper to parse pose data from DB (blob or string) and format it."""
        try:
            if isinstance(pose_data, bytes):
                if len(pose_data) == 12 * 4:  # 12 floats
                    values = struct.unpack('12f', pose_data)
                    logger.debug(f"Unpacked 12 floats for node {node_id}: {values}")
                elif len(pose_data) == 12 * 8:  # 12 doubles
                    values = struct.unpack('12d', pose_data)
                    logger.debug(f"Unpacked 12 doubles for node {node_id}: {values}")
                else:
                    logger.warning(f"Skipping node {node_id}: Pose data BLOB has unexpected length: {len(pose_data)}")
                    return None
            elif isinstance(pose_data, str):
                values = [float(x) for x in pose_data.split()]
                if len(values) != 12:
                    logger.warning(f"Skipping node {node_id}: Pose data string has wrong number of values: {len(values)}")
                    return None
            else:
                logger.warning(f"Skipping node {node_id}: Unknown pose data type: {type(pose_data)}")
                return None

            # RTAB-Map Pose Format (12 values):
            # [r11 r12 r13] x y z [r21 r22 r23] [r31 r32 r33]
            #  0   1   2   3 4 5  6   7   8   9  10  11
            # Correct parsing:
            r11, r12, r13 = values[0], values[1], values[2]      # Row 1 of rotation matrix
            tx, ty, tz = values[3], values[4], values[5]          # Translation (x, y, z)
            r21, r22, r23 = values[6], values[7], values[8]      # Row 2 of rotation matrix
            r31, r32, r33 = values[9], values[10], values[11]    # Row 3 of rotation matrix
            
            logger.debug(f"Translation values for node {node_id}: tx={tx}, ty={ty}, tz={tz}")
            
            # Convert rotation matrix to quaternion, then to Euler angles (roll, pitch, yaw)
            qx, qy, qz, qw = rotation_matrix_to_quaternion(r11, r12, r13, r21, r22, r23, r31, r32, r33)
            roll, pitch, yaw = quaternion_to_rpy(qx, qy, qz, qw)
            
            # Return the formatted pose dictionary
            result = {
                "x": round(tx, 2),
                "y": round(ty, 2),
                "z": round(tz, 2), 
                "roll": round(roll, precision), 
                "pitch": round(pitch, precision), 
                "yaw": round(yaw, precision)
            }
            logger.debug(f"Final formatted pose for node {node_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error processing pose for node {node_id}: {e}")
            return None

    async def get_stored_node_pose(self, node_id: int) -> Optional[dict]:
        """
        Retrieves the GLOBAL pose from metadata and includes object descriptions.
        
        IMPORTANT: This returns GLOBAL coordinates from the optimized pose graph,
        not relative coordinates from the Node table.
        
        Returns coordinates in meters from the global reference frame.
        """
        if not self.db_path:
            logger.error("Database path not set")
            return None
            
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get global coordinates from metadata
            global_pose = get_frame_global_coordinates(cursor, node_id)
            
            if not global_pose:
                logger.error(f"No global coordinates found for node {node_id}")
                conn.close()
                return None
            
            # Start with global pose data
            parsed_pose = {
                "x": round(global_pose['x'], 2),
                "y": round(global_pose['y'], 2),
                "z": round(global_pose['z'], 2),
                "roll": round(global_pose['roll'], 5),
                "pitch": round(global_pose['pitch'], 5),
                "yaw": round(global_pose['yaw'], 5)
            }
            
            logger.debug(f"Global coordinates for node {node_id}: x={parsed_pose['x']}, y={parsed_pose['y']}, z={parsed_pose['z']}")
            
            # Query for object metadata from ObjMeta table
            try:
                cursor.execute("SELECT metadata_json FROM ObjMeta WHERE frame_id = ?", (node_id,))
                metadata_result = cursor.fetchone()
                
                if metadata_result and metadata_result[0]:
                    # Parse the JSON metadata
                    metadata = json.loads(metadata_result[0])
                    
                    # Extract objects list (handle both dict and list formats)
                    if isinstance(metadata, dict):
                        objects = metadata.get('objects', [])
                    elif isinstance(metadata, list):
                        objects = metadata
                    else:
                        objects = []
                    
                    # Format objects as a readable string
                    object_descriptions = []
                    for obj in objects:
                        class_name = obj.get("class_name", "Unknown")
                        notes = obj.get("notes", "No description available")
                        formatted_obj = f"{class_name}: {notes}"
                        object_descriptions.append(formatted_obj)

                    # Join all objects with " •• " separator
                    objects_string = " •• ".join(object_descriptions)
                    parsed_pose["objects"] = objects_string
                    logger.info(f"Added {len(objects)} objects metadata for node {node_id}")
                else:
                    # No metadata found, set empty string
                    parsed_pose["objects"] = ""
                    logger.debug(f"No object metadata found for node {node_id}")
                    
            except sqlite3.Error as meta_error:
                # ObjMeta table might not exist or other DB error
                logger.warning(f"Could not fetch object metadata for node {node_id}: {meta_error}")
                parsed_pose["objects"] = ""
            except json.JSONDecodeError as json_error:
                # Invalid JSON in metadata
                logger.warning(f"Invalid JSON in metadata for node {node_id}: {json_error}")
                parsed_pose["objects"] = ""
            
            conn.close()
            logger.info(f"Successfully retrieved GLOBAL pose for node {node_id}: x={parsed_pose['x']}, y={parsed_pose['y']}, z={parsed_pose['z']}")
            return parsed_pose
        except Exception as e:
            logger.error(f"Error querying database for node {node_id}: {e}")
            if 'conn' in locals():
                conn.close()
            return None

    async def initialize(self, db_path_obj: Path) -> bool:
        """
        Initialize the RTAB-Map service with a specific database.
        
        Args:
            db_path_obj: Path to the RTAB-Map database file
            
        Returns:
            True if initialization successful, False otherwise
        """
        async with self.lock:
            # If service is already initialized with the same DB, no need to reinitialize
            if self.is_initialized and self.db_path == db_path_obj:
                logger.info(f"RTAB-Map service already initialized with database: {db_path_obj}")
                return True

            # Shut down any existing service before initializing a new one
            await self.shutdown() # Resets flags

            logger.info(f"Initializing RTAB-Map service with database: {db_path_obj}")
            if not db_path_obj.is_file():
                logger.error(f"Database file not found: {db_path_obj}")
                return False
            self.db_path = db_path_obj

            # RTAB-Map Console Parameters - Optimized for High-Performance Headless Localization
            # Based on GitHub Issues #1528, #358, #1507 analysis for API workloads
            self.base_rtabmap_params = [
                # === CORE DATABASE AND MEMORY CONFIGURATION ===
                "--Rtabmap/LoadDatabaseParameters", "false",   # Override database params with our explicit settings
                "--Mem/IncrementalMemory", "false",             # Use localization mode (no new map creation)
                "--Mem/InitWMWithAllNodes", "true",             # Load ALL database nodes into Working Memory at startup
                
                # === PERFORMANCE OPTIMIZATIONS - HEADLESS OPERATION ===
                # Detection Rate Optimization (Issue #358): Conservative increase for stability
                "--Rtabmap/DetectionRate", "1.0",               # Default detection rate for better accuracy
                "--Rtabmap/TimeThr", "300",                     # Reduce from default 700ms to 300ms
                
                # === MEMORY MANAGEMENT - OPTIMIZED FOR HEADLESS (Issue #358: 90% CPU, 70% RAM savings) ===
                "--Mem/STMSize", "0",                           # Disable Short-Term Memory size limit (keep all nodes)
                "--Mem/MemoryThr", "0",                         # Disable automatic transfer to Long-Term Memory
                "--Mem/RehearsalSimilarity", "0.0",             # Disable similarity-based memory rehearsal
                "--Mem/ImageKept", "false",                     # Don't store raw images (major RAM savings)
                "--Mem/BinDataKept", "false",                   # Don't store raw binary data (major RAM savings)
                "--Mem/RawDescriptorsKept", "true",             # Keep feature descriptors for matching
                
                # === GRID OPTIMIZATION - SKIP UNNECESSARY PROCESSING ===
                "--RGBD/CreateOccupancyGrid", "false",          # Skip occupancy grid generation (major speedup)
                "--Grid/FromDepth", "false",                    # Don't generate grids from depth (headless optimization)
                
                # === SIFT FEATURE DETECTION - OPTIMIZED FOR CAMERA IMAGES ===
                "--Kp/DetectorStrategy", "1",                   # Use SIFT keypoint detector (deterministic)
                "--Vis/FeatureType", "1",                       # Use SIFT feature descriptors
                "--SIFT/ContrastThreshold", "0.02",             # LOWERED from 0.04 - Extracts more features (less selective)
                "--SIFT/EdgeThreshold", "10",                   # SIFT edge threshold (filters edge-like features)
                "--SIFT/NOctaveLayers", "3",                    # Number of octave layers in SIFT pyramid
                "--SIFT/Sigma", "1.6",                          # Gaussian blur sigma for SIFT
                "--SIFT/Gpu", "false",                          # Force CPU processing (more deterministic than GPU)
                "--SIFT/PreciseUpscale", "false",               # Disable precise upscaling
                "--SIFT/RootSIFT", "false",                     # Disable RootSIFT normalization
                "--SIFT/Upscale", "false",                      # Disable image upscaling before detection
                
                # === FEATURE EXTRACTION OPTIMIZATION - INCREASED FOR CAMERA MATCHING ===
                "--Kp/MaxFeatures", "2000",                     # INCREASED from 1000 - Extract more features for better matching
                "--Vis/MaxFeatures", "2000",                    # Match keypoint features
                
                # === SPATIAL GRID PARAMETERS - CRITICAL FOR DETERMINISM ===
                "--Kp/GridCols", "1",                          # Single column grid (no spatial subdivision)
                "--Kp/GridRows", "1",                          # Single row grid (extract from entire image)
                "--Kp/RoiRatios", "0.0 0.0 0.0 0.0",          # No Region of Interest filtering
                
                # === LOOP CLOSURE AND MATCHING THRESHOLDS - RELAXED FOR CAMERA MATCHING ===
                "--Rtabmap/LoopThr", "0.08",                   # LOWERED from 0.11 - More lenient loop closure threshold for camera images
                "--Vis/MinInliers", "15",                      # LOWERED from 20 - Accept matches with fewer inliers
                "--Vis/InlierDistance", "0.1",                 # Maximum distance for RANSAC inliers
                "--Vis/CorNNDR", "0.8",                        # Nearest Neighbor Distance Ratio for feature matching
                "--Vis/RefineIterations", "5",                 # RANSAC refinement iterations
                
                # === FEATURE CORRESPONDENCE PARAMETERS ===
                "--Vis/CorType", "0",                          # Use brute force matching (most deterministic)
                "--Vis/CorGuessWinSize", "0",                  # Disable correlation window (eliminates randomness)
                "--Vis/CorNNType", "1",                        # Nearest neighbor search type
                
                # === SUBPIXEL REFINEMENT - DETERMINISTIC CONFIGURATION ===
                "--Kp/SubPixWinSize", "3",                     # Subpixel refinement window size for keypoints
                "--Vis/SubPixWinSize", "3",                    # Subpixel refinement window size for visual features
                "--Kp/SubPixEps", "0.02",                      # Subpixel refinement convergence epsilon
                "--Vis/SubPixEps", "0.02",                     # Visual subpixel refinement epsilon
                "--Kp/SubPixIterations", "0",                  # DISABLE subpixel iterations (source of randomness)
                "--Vis/SubPixIterations", "0",                 # DISABLE visual subpixel iterations
                
                # === IMAGE PREPROCESSING ===
                "--Mem/ImagePreDecimation", "2",               # Downsample images by factor of 2 before processing
                "--Mem/ImagePostDecimation", "1",              # No post-processing decimation
                
                # === RANDOMNESS ELIMINATION - CRITICAL FOR DETERMINISTIC RESULTS ===
                "--Kp/Parallelized", "false",                  # Disable parallel processing (thread-order randomness)
                "--Vis/SSC", "false",                          # Disable Suppression via Square Covering (randomness)
                "--Kp/SSC", "false",                           # Disable SSC for keypoints
                "--Kp/NewWordsComparedTogether", "true",       # Compare new words deterministically
                "--Kp/IncrementalFlann", "false",              # Disable incremental FLANN (rebuilds can vary)
                
                # === NEAREST NEIGHBOR SEARCH CONFIGURATION ===
                "--Kp/FlannRebalancingFactor", "2.0",          # FLANN tree rebalancing factor
                "--Kp/NNStrategy", "1",                        # Use FLANN for nearest neighbor search
                
                # === GRAPH OPTIMIZATION - COMPATIBLE OPTIMIZATION FOR LOCALIZATION ===
                # Note: Use g2o optimizer which works better with this database type
                "--Optimizer/Strategy", "1",                    # Use g2o optimization (better compatibility)
                "--Optimizer/Iterations", "3",                  # Light optimization iterations (vs default 10)
                "--RGBD/OptimizeMaxError", "0.1",               # More tolerant error threshold
                
                # === MULTI-THREADING CONTROL - DETERMINISTIC PERFORMANCE (Issue #358) ===
                "--Kp/Parallelized", "false",                   # Force single-threaded (eliminates variable 150-500ms performance)
                
                # === PROXIMITY-BASED OPTIMIZATIONS (Issue #1507: RAM Efficiency) ===
                "--Mem/RehearsalWeightIgnoredWhileMoving", "true", # Skip rehearsal during active localization
                "--Rtabmap/MaxRetrieved", "100",                # Limit retrieved nodes for proximity matching
                
                # === POSE ESTIMATION (RANSAC) PARAMETERS ===
                "--Vis/PnPFlags", "0",                         # PnP solver flags
                "--Vis/PnPReprojError", "2",                   # Maximum reprojection error for PnP
                "--Vis/EstimationType", "1",                   # Motion estimation type
                
                # === FINAL OPTIMIZATION AND GRAPH PARAMETERS ===
                "--RGBD/ProximityPathMaxNeighbors", "0",       # Disable proximity path neighbors
                "--RGBD/NeighborLinkRefining", "false",        # Disable neighbor link refinement
                
                # === LOGGING AND OUTPUT CONFIGURATION ===
                "--Rtabmap/StatisticLogged", "true",           # Enable comprehensive statistics logging
                "--Rtabmap/StatisticLoggedHeaders", "true",    # Include headers in statistics
                "--Rtabmap/PublishLastLocalizationPose", "false", # Don't publish poses (we extract manually)
                "--Mem/LaserScanDownsampleStep", "1",          # No laser scan downsampling
                "--Mem/NotLinkedNodesKept", "false",           # Remove unlinked nodes from memory
                "--Rtabmap/ImagesAlreadyRectified", "true",    # Skip image rectification (assume pre-rectified)
                
                # === CONSOLE OUTPUT CONFIGURATION ===
                "--logconsole",                                # Enable console logging
                "--uinfo"                                      # Set log level to INFO for detailed output
            ]

            # The service is now considered "initialized" and ready for processing.
            logger.info("RTAB-Map service initialized and ready for processing.")
            self.is_initialized = True
            return True

    async def process_image(self, image_path: Path) -> Dict:
        """
        Process an image for localization against the loaded database.
        
        Args:
            image_path: Path to the image file to process
            
        Returns:
            Dictionary containing localization results
        """
        if not self.is_initialized or not self.db_path:
            raise RuntimeError("RTAB-Map service not initialized or DB path not set.")

        async with self.lock:
            # Create a temporary directory for processing
            self.image_counter += 1
            request_id = f"req_{self.image_counter}_{int(time.time())}"
            image_processing_dir = DATA_DIR / f"temp_proc_{request_id}"
            image_name = image_path.name
            start_time_total = time.perf_counter()
            
            try:
                # Prepare the processing directory
                image_processing_dir.mkdir(parents=True, exist_ok=True)
                target_image_in_processing_dir = image_processing_dir / image_name
                shutil.copy(image_path, target_image_in_processing_dir)

                # Run localization with base parameters
                per_image_cmd = ["rtabmap-console", "-input", str(self.db_path)] + self.base_rtabmap_params + [str(image_processing_dir)]
                logger.info(f"Running command: {' '.join(per_image_cmd)}")
                proc_img_loc = await asyncio.create_subprocess_exec(*per_image_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                stdout_bytes, stderr_bytes = await asyncio.wait_for(proc_img_loc.communicate(), timeout=60.0)
                output_text_localization = stdout_bytes.decode(errors='ignore') + stderr_bytes.decode(errors='ignore')
                
                logger.info(f"RTAB-Map command completed with return code: {proc_img_loc.returncode}")
                logger.info(f"FULL RTAB-Map output:\n{output_text_localization}")
                
                if proc_img_loc.returncode != 0:
                    logger.error(f"RTAB-Map processing failed for {image_name}. RC={proc_img_loc.returncode}")
                
                logger.info("About to call parse_localization_output...")
                try:
                    final_pose_data = parse_localization_output(output_text_localization)
                    logger.info(f"parse_localization_output returned: {final_pose_data}")
                except Exception as e:
                    logger.error(f"Exception in parse_localization_output: {e}")
                    final_pose_data = None

                if final_pose_data:
                    pic_id_matched = final_pose_data.get("pic_id")
                    if pic_id_matched is not None and final_pose_data.get("localization_successful"):
                        logger.info(f"Attempting to retrieve stored GLOBAL pose for pic_id {pic_id_matched}")
                        stored_pose = await self.get_stored_node_pose(pic_id_matched)
                        if stored_pose:
                            # Use the stored GLOBAL pose and add the additional metadata
                            # CRITICAL: stored_pose contains GLOBAL coordinates from ObjMeta
                            logger.info(f"Retrieved GLOBAL coordinates: X={stored_pose.get('x'):.3f}, Y={stored_pose.get('y'):.3f}, Z={stored_pose.get('z'):.3f}")
                            
                            # Build result with GLOBAL coordinates
                            final_pose_data = {
                                "localization_successful": True,
                                "pic_id": pic_id_matched,
                                "hypothesis_value": final_pose_data.get("hypothesis_value"),
                                # GLOBAL POSITION (from ObjMeta database)
                                "x": stored_pose.get("x", 0),
                                "y": stored_pose.get("y", 0),
                                "z": stored_pose.get("z", 0),
                                # GLOBAL ORIENTATION
                                "roll": stored_pose.get("roll", 0),
                                "pitch": stored_pose.get("pitch", 0),
                                "yaw": stored_pose.get("yaw", 0),
                                # OBJECT METADATA
                                "objects": stored_pose.get("objects", ""),
                                # PROCESSING METADATA
                                "image_name": image_name,
                                "elapsed_ms": int((time.perf_counter() - start_time_total) * 1000)
                            }
                            logger.info(f"Successfully retrieved GLOBAL pose for frame {pic_id_matched}")
                            return final_pose_data
                        else:
                            logger.error(f"Failed to get GLOBAL pose for pic_id {pic_id_matched}")
                            return {
                                "error": f"Failed to retrieve GLOBAL coordinates for matched image {pic_id_matched}",
                                "image_name": image_name,
                                "elapsed_ms": int((time.perf_counter() - start_time_total) * 1000)
                            }
                
                    raise RuntimeError(f"No valid localization match found for {image_name}")

                raise RuntimeError(f"Failed to get localization results for {image_name}.")

            except (TimeoutError, RuntimeError, Exception) as e:
                logger.exception(f"Error processing {image_name}: {e}")
                return {
                    "error": f"{type(e).__name__}: {e}", 
                    "image_name": image_name, 
                    "elapsed_ms": int((time.perf_counter() - start_time_total) * 1000)
                }
            finally:
                # Always clean up the temporary directory
                if image_processing_dir.exists():
                    try:
                        shutil.rmtree(image_processing_dir)
                        logger.debug(f"Removed directory: {image_processing_dir}")
                    except Exception as e:
                        logger.error(f"Error removing directory {image_processing_dir}: {e}")

    async def shutdown(self):
        """
        Shutdown the RTAB-Map service and clean up resources.
        """
        logger.info("Shutting down RTAB-Map service...")
        
        # Reset service state
        self.db_path = None
        self.is_initialized = False
        logger.info("RTAB-Map service shutdown complete.")

    def get_status(self) -> Dict:
        """
        Get current status of the RTAB-Map service.
        
        Returns:
            Dictionary with service status information
        """
        return {
            "initialized": self.is_initialized,
            "database_path": str(self.db_path) if self.db_path else None,
            "image_counter": self.image_counter
        }
