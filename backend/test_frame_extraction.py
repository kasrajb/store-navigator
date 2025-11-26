"""
Frame Extraction Module for Route Details

This module provides functions to extract intermediate frame images between
user location and target destination for landmark-based navigation.

Functionality:
1. Calculate intermediate frames along the route
2. Extract frame images from RTAB-Map database
3. Encode images to Base64 format
4. Generate complete route_details structure

Requirements:
- RTAB-Map database with Data table containing image BLOBs
- OpenCV for image decompression
- Base64 encoding support
"""

import sqlite3
import cv2
import numpy as np
import base64
import logging
import math
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def calculate_intermediate_frames(
    start_frame_id: int,
    end_frame_id: int,
    start_position: Dict[str, float],
    end_position: Dict[str, float],
    db_path: str,
    num_frames: int = 5
) -> List[int]:
    """
    Calculate intermediate frame IDs between start and end positions.
    
    NOTE: num_frames is capped at 5 maximum middle frames.
    If num_frames > 5, it will be reduced to 5.
    """
    # Cap at maximum 5 middle frames
    num_frames = min(num_frames, 5)
    """
    Calculate intermediate frame IDs between start and end positions.
    
    Strategy:
    1. Calculate the straight-line distance between start and end
    2. Divide the distance into equal segments (num_frames)
    3. For each segment, query database for nearest frame to that position
    4. Return ordered list of frame IDs along the route
    
    Args:
        start_frame_id: Frame ID of user's current location
        end_frame_id: Frame ID of target destination
        start_position: Dict with 'x', 'y' keys (user position)
        end_position: Dict with 'x', 'y' keys (target position)
        db_path: Path to RTAB-Map database
        num_frames: Number of intermediate frames to extract (default 5)
        
    Returns:
        List of frame IDs ordered from start to end
        
    Example:
        User at Frame 80 (x=3.67, y=-2.22)
        Target at Frame 464 (x=6.60, y=-37.06)
        → Returns [80, 150, 250, 350, 420, 464] (6 frames including start/end)
    """
    logger.info(f"Calculating {num_frames} intermediate frames from {start_frame_id} to {end_frame_id}")
    logger.info(f"Start position: {start_position}, End position: {end_position}")
    
    # Always include start and end frames
    intermediate_frames = [start_frame_id]
    
    # If start and end are the same, return single frame
    if start_frame_id == end_frame_id:
        logger.info("Start and end frames are identical")
        return intermediate_frames
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Calculate total distance and step size
        dx = end_position['x'] - start_position['x']
        dy = end_position['y'] - start_position['y']
        total_distance = math.sqrt(dx**2 + dy**2)
        
        logger.info(f"Total distance: {total_distance:.2f} meters")
        
        # If distance is very short (<1m), just return start and end
        if total_distance < 1.0:
            logger.info("Distance too short for intermediate frames")
            intermediate_frames.append(end_frame_id)
            return intermediate_frames
        
        # Calculate step positions along the route
        for i in range(1, num_frames + 1):
            # Calculate interpolation ratio
            ratio = i / (num_frames + 1)
            
            # Interpolate position
            target_x = start_position['x'] + (dx * ratio)
            target_y = start_position['y'] + (dy * ratio)
            
            logger.debug(f"Searching for frame near position ({target_x:.2f}, {target_y:.2f})")
            
            # Query database for nearest frame to this position
            # Use ObjMeta table with global coordinates
            query = """
            SELECT frame_id, 
                   json_extract(metadata_json, '$.global_pose.x') as x,
                   json_extract(metadata_json, '$.global_pose.y') as y,
                   (json_extract(metadata_json, '$.global_pose.x') - ?) * 
                   (json_extract(metadata_json, '$.global_pose.x') - ?) +
                   (json_extract(metadata_json, '$.global_pose.y') - ?) * 
                   (json_extract(metadata_json, '$.global_pose.y') - ?) as distance_sq
            FROM ObjMeta
            WHERE x IS NOT NULL AND y IS NOT NULL
            ORDER BY distance_sq ASC
            LIMIT 1
            """
            
            cursor.execute(query, (target_x, target_x, target_y, target_y))
            result = cursor.fetchone()
            
            if result:
                nearest_frame_id = result[0]
                frame_x = result[1]
                frame_y = result[2]
                distance = math.sqrt(result[3])
                
                logger.debug(f"Found Frame {nearest_frame_id} at ({frame_x:.2f}, {frame_y:.2f}), distance: {distance:.2f}m")
                
                # Avoid duplicate frames
                if nearest_frame_id not in intermediate_frames:
                    intermediate_frames.append(nearest_frame_id)
            else:
                logger.warning(f"No frame found near position ({target_x:.2f}, {target_y:.2f})")
        
        # Always add end frame
        if end_frame_id not in intermediate_frames:
            intermediate_frames.append(end_frame_id)
        
        conn.close()
        
        logger.info(f"Selected {len(intermediate_frames)} frames: {intermediate_frames}")
        return intermediate_frames
        
    except Exception as e:
        logger.error(f"Error calculating intermediate frames: {e}")
        # Fallback: return just start and end frames
        return [start_frame_id, end_frame_id]


def extract_frame_image_from_database(frame_id: int, db_path: str) -> Optional[np.ndarray]:
    """
    Extract and decompress image from RTAB-Map database.
    
    The Data table stores images as compressed BLOBs (JPEG/PNG format).
    This function:
    1. Queries the Data table for the frame's image BLOB
    2. Decompresses the BLOB using OpenCV
    3. Returns the decompressed image as a numpy array
    
    Args:
        frame_id: Frame ID to extract image for
        db_path: Path to RTAB-Map database
        
    Returns:
        Numpy array (OpenCV image) if successful, None if failed
        
    Example:
        image = extract_frame_image_from_database(80, "corridor-V3.db")
        # Returns: numpy array of shape (480, 640, 3) for RGB image
    """
    logger.debug(f"Extracting image for Frame {frame_id} from database")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query the Data table for the compressed image BLOB
        cursor.execute("SELECT image FROM Data WHERE id = ?", (frame_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            logger.warning(f"No image data found for Frame {frame_id}")
            conn.close()
            return None
        
        # Get the compressed image BLOB
        image_blob = result[0]
        conn.close()
        
        logger.debug(f"Retrieved image BLOB of size {len(image_blob)} bytes")
        
        # Decompress the image using OpenCV
        # cv2.imdecode handles various compression formats (JPEG, PNG, etc.)
        image_array = np.frombuffer(image_blob, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.error(f"Failed to decompress image for Frame {frame_id}")
            return None
        
        logger.debug(f"Successfully decompressed image: shape={image.shape}, dtype={image.dtype}")
        return image
        
    except Exception as e:
        logger.error(f"Error extracting image for Frame {frame_id}: {e}")
        return None


def encode_image_to_base64(image: np.ndarray, format: str = "JPEG", quality: int = 85) -> Optional[str]:
    """
    Encode OpenCV image to Base64 string for API transmission.
    
    Args:
        image: OpenCV image (numpy array)
        format: Image format for encoding ("JPEG" or "PNG")
        quality: JPEG quality (0-100), ignored for PNG
        
    Returns:
        Base64-encoded string (with data URI prefix) or None if encoding failed
        
    Example:
        base64_str = encode_image_to_base64(image, format="JPEG", quality=85)
        # Returns: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
    """
    logger.debug(f"Encoding image to Base64 (format={format}, quality={quality})")
    
    try:
        # Compress image to desired format
        if format.upper() == "JPEG":
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
            extension = ".jpg"
            mime_type = "image/jpeg"
        elif format.upper() == "PNG":
            encode_params = [cv2.IMWRITE_PNG_COMPRESSION, 3]  # 0-9, higher = more compression
            extension = ".png"
            mime_type = "image/png"
        else:
            logger.error(f"Unsupported image format: {format}")
            return None
        
        # Encode image to bytes
        success, encoded_image = cv2.imencode(extension, image, encode_params)
        
        if not success:
            logger.error(f"Failed to encode image to {format}")
            return None
        
        # Convert to Base64 string
        image_bytes = encoded_image.tobytes()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        # Add data URI prefix for web compatibility
        data_uri = f"data:{mime_type};base64,{base64_string}"
        
        logger.debug(f"Successfully encoded image: {len(data_uri)} characters")
        return data_uri
        
    except Exception as e:
        logger.error(f"Error encoding image to Base64: {e}")
        return None


def generate_route_details(
    user_frame_id: int,
    target_frame_id: int,
    user_position: Dict[str, float],
    target_position: Dict[str, float],
    db_path: str,
    num_intermediate_frames: int = 5,
    image_format: str = "JPEG",
    image_quality: int = 75
) -> Dict:
    """
    Generate complete route_details structure with intermediate frame images.
    
    This is the main function that orchestrates the entire route extraction process:
    1. Calculate intermediate frames along the route
    2. Extract images for each frame from database
    3. Encode images to Base64
    4. Package everything into the response structure
    
    Args:
        user_frame_id: Frame ID of user's current location
        target_frame_id: Frame ID of target destination
        user_position: Dict with 'x', 'y' keys (user position in meters)
        target_position: Dict with 'x', 'y' keys (target position in meters)
        db_path: Path to RTAB-Map database
        num_intermediate_frames: Number of intermediate frames to include (default 5)
        image_format: Image encoding format ("JPEG" or "PNG", default "JPEG")
        image_quality: JPEG quality 0-100 (default 75 for balance of size/quality)
        
    Returns:
        Dictionary with structure:
        {
            "total_frames": int,
            "frames": [
                {
                    "frame_id": int,
                    "position": {"x": float, "y": float},
                    "distance_from_start": float,
                    "image_base64": str
                },
                ...
            ],
            "route_distance": float,
            "frame_extraction_success": bool,
            "error_message": str (optional)
        }
        
    Example:
        route_details = generate_route_details(
            user_frame_id=80,
            target_frame_id=464,
            user_position={"x": 3.67, "y": -2.22},
            target_position={"x": 6.60, "y": -37.06},
            db_path="/data/database.db",
            num_intermediate_frames=5
        )
    """
    logger.info("="*80)
    logger.info("GENERATING ROUTE DETAILS WITH INTERMEDIATE FRAMES")
    logger.info("="*80)
    logger.info(f"Route: Frame {user_frame_id} → Frame {target_frame_id}")
    logger.info(f"Start Position: {user_position}")
    logger.info(f"End Position: {target_position}")
    logger.info(f"Intermediate Frames: {num_intermediate_frames}")
    logger.info(f"Image Format: {image_format}, Quality: {image_quality}")
    
    try:
        # Step 1: Calculate intermediate frame IDs
        frame_ids = calculate_intermediate_frames(
            start_frame_id=user_frame_id,
            end_frame_id=target_frame_id,
            start_position=user_position,
            end_position=target_position,
            db_path=db_path,
            num_frames=num_intermediate_frames
        )
        
        logger.info(f"Selected {len(frame_ids)} frames along route: {frame_ids}")
        
        # Step 2: Extract and encode images for each frame
        frames_data = []
        failed_frames = []
        
        # Calculate total route distance
        dx = target_position['x'] - user_position['x']
        dy = target_position['y'] - user_position['y']
        total_distance = math.sqrt(dx**2 + dy**2)
        
        for frame_id in frame_ids:
            logger.info(f"Processing Frame {frame_id}...")
            
            # Get frame coordinates from database
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT json_extract(metadata_json, '$.global_pose.x') as x,
                           json_extract(metadata_json, '$.global_pose.y') as y
                    FROM ObjMeta WHERE frame_id = ?
                """, (frame_id,))
                result = cursor.fetchone()
                conn.close()
                
                if not result:
                    logger.warning(f"No metadata found for Frame {frame_id}")
                    failed_frames.append(frame_id)
                    continue
                
                frame_x, frame_y = result[0], result[1]
                
            except Exception as e:
                logger.error(f"Error querying metadata for Frame {frame_id}: {e}")
                failed_frames.append(frame_id)
                continue
            
            # Calculate distance from start
            distance_from_start = math.sqrt(
                (frame_x - user_position['x'])**2 + 
                (frame_y - user_position['y'])**2
            )
            
            # Extract image from database
            image = extract_frame_image_from_database(frame_id, db_path)
            
            if image is None:
                logger.warning(f"Failed to extract image for Frame {frame_id}")
                failed_frames.append(frame_id)
                continue
            
            # Encode image to Base64
            base64_image = encode_image_to_base64(image, format=image_format, quality=image_quality)
            
            if base64_image is None:
                logger.warning(f"Failed to encode image for Frame {frame_id}")
                failed_frames.append(frame_id)
                continue
            
            # Add frame data to result (without image_base64 to save space - images are in separate array)
            frame_data = {
                "frame_id": frame_id,
                "position": {
                    "x": round(frame_x, 2),
                    "y": round(frame_y, 2)
                },
                "distance_from_start": round(distance_from_start, 2)
            }
            
            frames_data.append(frame_data)
            logger.info(f"✓ Frame {frame_id} processed successfully (distance: {distance_from_start:.2f}m)")
        
        # Step 3: Generate final response
        success = len(frames_data) > 0
        
        # Extract just the Base64 images into a simple list for vision pipeline
        images_only = []
        for frame in frames_data:
            if frame.get("image_base64"):
                images_only.append(frame["image_base64"])
            else:
                images_only.append(None)
        
        logger.info(f"Extracted {len(images_only)} images for simple array")
        
        result = {
            "total_frames": len(frames_data),
            "frames": frames_data,
            "route_distance": round(total_distance, 2),
            "frame_extraction_success": success,
            "images": images_only
        }
        
        if failed_frames:
            result["error_message"] = f"Failed to extract {len(failed_frames)} frames: {failed_frames}"
            logger.warning(result["error_message"])
        
        logger.info("="*80)
        logger.info(f"ROUTE DETAILS GENERATION COMPLETE")
        logger.info(f"Total Frames: {len(frames_data)}/{len(frame_ids)}")
        logger.info(f"Route Distance: {total_distance:.2f} meters")
        logger.info(f"Success: {success}")
        logger.info("="*80)
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating route details: {e}")
        return {
            "total_frames": 0,
            "frames": [],
            "route_distance": 0.0,
            "frame_extraction_success": False,
            "error_message": f"Route generation failed: {str(e)}"
        }


# --- Test Functions ---

def test_frame_extraction():
    """
    Test function to verify frame extraction works correctly.
    
    Tests the complete pipeline:
    1. Extract image from database
    2. Encode to Base64
    3. Verify the result is valid
    """
    print("="*80)
    print("TESTING FRAME EXTRACTION")
    print("="*80)
    
    # Configuration
    db_path = r"C:\Users\kasra\Desktop\Kasra\Telegram\rtabmap_api\data\database\corridor-V3.db"
    test_frame_id = 80  # Known frame with image
    
    print(f"\nTest 1: Extract image for Frame {test_frame_id}")
    image = extract_frame_image_from_database(test_frame_id, db_path)
    
    if image is not None:
        print(f"✓ Image extracted successfully")
        print(f"  Shape: {image.shape}")
        print(f"  Dtype: {image.dtype}")
        print(f"  Size: {image.nbytes / 1024:.1f} KB")
        
        print(f"\nTest 2: Encode image to Base64")
        base64_str = encode_image_to_base64(image, format="JPEG", quality=85)
        
        if base64_str:
            print(f"✓ Base64 encoding successful")
            print(f"  Length: {len(base64_str)} characters")
            print(f"  Prefix: {base64_str[:50]}...")
            
            # Verify it's a valid data URI
            if base64_str.startswith("data:image/"):
                print(f"✓ Valid data URI format")
            else:
                print(f"✗ Invalid data URI format")
        else:
            print(f"✗ Base64 encoding failed")
    else:
        print(f"✗ Image extraction failed")
    
    print("\n" + "="*80)


def test_intermediate_frames():
    """
    Test function to verify intermediate frame calculation.
    
    Uses real coordinates from the system:
    - User at Frame 80: (3.67, -2.22)
    - Target at Frame 464: (6.60, -37.06)
    """
    print("="*80)
    print("TESTING INTERMEDIATE FRAME CALCULATION")
    print("="*80)
    
    db_path = r"C:\Users\kasra\Desktop\Kasra\Telegram\rtabmap_api\data\database\corridor-V3.db"
    
    user_frame_id = 80
    target_frame_id = 464
    user_position = {"x": 3.67, "y": -2.22}
    target_position = {"x": 6.60, "y": -37.06}
    
    print(f"\nCalculating route from Frame {user_frame_id} to Frame {target_frame_id}")
    print(f"Start: ({user_position['x']}, {user_position['y']})")
    print(f"End: ({target_position['x']}, {target_position['y']})")
    
    frame_ids = calculate_intermediate_frames(
        start_frame_id=user_frame_id,
        end_frame_id=target_frame_id,
        start_position=user_position,
        end_position=target_position,
        db_path=db_path,
        num_frames=5
    )
    
    print(f"\nSelected {len(frame_ids)} frames:")
    for i, frame_id in enumerate(frame_ids):
        if i == 0:
            marker = "(START)"
        elif i == len(frame_ids) - 1:
            marker = "(END)"
        else:
            marker = f"(Intermediate {i})"
        print(f"  {i+1}. Frame {frame_id} {marker}")
    
    print("\n" + "="*80)


def test_route_details_generation():
    """
    Test the complete route_details generation pipeline.
    
    This is the integration test that verifies all components work together.
    """
    print("="*80)
    print("TESTING COMPLETE ROUTE DETAILS GENERATION")
    print("="*80)
    
    db_path = r"C:\Users\kasra\Desktop\Kasra\Telegram\rtabmap_api\data\database\corridor-V3.db"
    
    user_frame_id = 80
    target_frame_id = 464
    user_position = {"x": 3.67, "y": -2.22}
    target_position = {"x": 6.60, "y": -37.06}
    
    print(f"\nGenerating route details from Frame {user_frame_id} to Frame {target_frame_id}")
    
    route_details = generate_route_details(
        user_frame_id=user_frame_id,
        target_frame_id=target_frame_id,
        user_position=user_position,
        target_position=target_position,
        db_path=db_path,
        num_intermediate_frames=3,  # Use fewer frames for faster testing
        image_format="JPEG",
        image_quality=75
    )
    
    print("\n--- Route Details Result ---")
    print(f"Total Frames: {route_details['total_frames']}")
    print(f"Route Distance: {route_details['route_distance']} meters")
    print(f"Success: {route_details['frame_extraction_success']}")
    
    if route_details.get('error_message'):
        print(f"Errors: {route_details['error_message']}")
    
    print("\nFrame Details:")
    for frame in route_details['frames']:
        print(f"  Frame {frame['frame_id']}: ({frame['position']['x']}, {frame['position']['y']}) - {frame['distance_from_start']}m from start")
        print(f"    Base64 image: {len(frame['image_base64'])} characters")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    """
    Run all tests when script is executed directly.
    """
    import sys
    
    # Configure logging for test mode
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    print("\n" + "="*80)
    print("FRAME EXTRACTION MODULE - TEST SUITE")
    print("="*80 + "\n")
    
    try:
        # Test 1: Basic frame extraction and Base64 encoding
        test_frame_extraction()
        print("\n")
        
        # Test 2: Intermediate frame calculation
        test_intermediate_frames()
        print("\n")
        
        # Test 3: Complete route generation
        test_route_details_generation()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
