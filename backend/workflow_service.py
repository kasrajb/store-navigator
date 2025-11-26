"""
Workflow Service Module

This module contains the WorkflowService class that orchestrates the search-and-loca            # Step 3: Automatically trigger localization (same as CLI script behavior)
            logger.info("Starting automatic localization...")
            localization_start_time = time.time()
            
            try:
                # Check if we're running in Docker container or standalone
                from pathlib import Path
                external_test_dir = Path("/external_testimage")
                
                if external_test_dir.exists():
                    # Running in Docker container - use direct processing
                    from app import get_test_image_path
                    test_image_path = get_test_image_path()
                    localization_result = await self.rtabmap_service.process_image(test_image_path)
                else:
                    # Running outside container - use API endpoint
                    import requests
                    response = requests.post("http://localhost:8040/localize", timeout=30)
                    if response.status_code == 200:
                        localization_result = response.json()
                        # Ensure it has the expected structure
                        if not localization_result.get("localization_successful"):
                            localization_result = None
                    else:
                        logger.error(f"API localization failed with status {response.status_code}")
                        localization_result = None
                
                localization_elapsed = (time.time() - localization_start_time) * 1000w.
It serves as shared business logic that can be used by both the FastAPI endpoint and the 
standalone CLI script, ensuring consistent behavior across both interfaces.
"""

import time
import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import existing functionality
from search_product import search_products
from rtabmap_service import RTABMapService

# Set up logging
logger = logging.getLogger("workflow_service")


class WorkflowService:
    """
    Shared service that orchestrates the search-and-localize workflow.
    
    Used by both the API endpoint and the standalone CLI script to ensure
    consistent behavior and eliminate code duplication.
    """
    
    def __init__(self, rtabmap_service: RTABMapService, database_path: str, metadata_db_path: str):
        """
        Initialize the workflow service.
        
        Args:
            rtabmap_service: Initialized RTABMapService instance
            database_path: Path to the RTAB-Map database file
            metadata_db_path: Path to the metadata database file (containing ObjMeta table)
        """
        self.rtabmap_service = rtabmap_service
        self.database_path = database_path
        self.metadata_db_path = metadata_db_path
    
    async def execute_workflow(self, object_name: str, include_timing: bool = True, image_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Execute the complete search-and-localize workflow.
        
        This method performs the same workflow as the CLI script but returns
        structured data instead of printing to the terminal.
        
        Args:
            object_name: The object to search for
            include_timing: Whether to include timing information in response
            image_path: Optional path to uploaded image. If None, uses test image from external directory
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating overall workflow success
            - search_results: List of matching products with locations
            - localization_results: Pose and object data from localization
            - total_matches: Number of search matches found
            - workflow_status: String description of workflow completion status
            - timing_ms: Performance metrics (if include_timing is True)
            - error_message: Error description (if workflow failed)
        """
        workflow_start_time = time.time()
        
        try:
            # Step 1: Validate RTAB-Map service is ready
            if not self.rtabmap_service or not self.rtabmap_service.is_initialized:
                return {
                    "success": False,
                    "search_results": [],
                    "localization_results": None,
                    "total_matches": 0,
                    "workflow_status": "rtabmap_service_not_initialized",
                    "timing_ms": None,
                    "error_message": "RTAB-Map service is not initialized"
                }
            
            # Step 2: Perform product search
            logger.info(f"Starting product search for: {object_name}")
            search_start_time = time.time()
            
            try:
                search_results = search_products(
                    search_term=object_name,
                    db_path=self.metadata_db_path,
                    use_sql_prefilter=True,
                    show_performance=False  # Disable print statements for API usage
                )
                search_elapsed = (time.time() - search_start_time) * 1000
                
                logger.info(f"Product search completed: {len(search_results)} matches found")
                
            except Exception as e:
                logger.error(f"Product search failed: {e}")
                return {
                    "success": False,
                    "search_results": [],
                    "localization_results": None,
                    "total_matches": 0,
                    "workflow_status": "search_failed",
                    "timing_ms": None,
                    "error_message": f"Product search failed: {str(e)}"
                }
            
            # Step 3: Convert search results to API format
            formatted_search_results = []
            for result in search_results:
                formatted_result = {
                    "frame_id": result['frame_id'],
                    "location": {
                        "x": result['x'],
                        "y": result['y']
                    },
                    "objects": result['objects']
                }
                formatted_search_results.append(formatted_result)
            
            # Step 4: Automatically trigger localization
            logger.info("Starting automatic localization...")
            localization_start_time = time.time()
            
            try:
                # Determine which image to use for localization
                if image_path:
                    # Use the provided uploaded image (webapp integration)
                    logger.info(f"Using uploaded image for localization: {image_path}")
                    target_image_path = image_path
                else:
                    # Fallback to test image from external directory (backward compatibility)
                    is_containerized = self._is_running_in_container()
                    
                    if is_containerized:
                        from app import get_test_image_path
                        target_image_path = get_test_image_path()
                        logger.info(f"Using test image from external directory: {target_image_path}")
                    else:
                        # Running outside container - call API endpoint
                        logger.info("Running outside container - using API endpoint for localization")
                        localization_result = await self._call_localization_api()
                        localization_elapsed = (time.time() - localization_start_time) * 1000
                        
                        if localization_result and localization_result.get("localization_successful"):
                            logger.info("Localization completed successfully via API")
                            
                            # CRITICAL: API response already contains GLOBAL coordinates
                            user_x = localization_result.get("x", 0)
                            user_y = localization_result.get("y", 0)
                            user_z = localization_result.get("z", 0)
                            
                            logger.info(f"User position from API localization: X={user_x:.3f}, Y={user_y:.3f}, Z={user_z:.3f}")
                            
                            # Format the API response into the expected structure
                            formatted_localization = {
                                "position": {
                                    "x": user_x,
                                    "y": user_y,
                                    "z": user_z
                                },
                                "orientation": {
                                    "roll": localization_result.get("roll", 0),
                                    "pitch": localization_result.get("pitch", 0),
                                    "yaw": localization_result.get("yaw", 0)
                                },
                                "detected_objects": localization_result.get("objects", ""),
                                "picture_id": localization_result.get("pic_id", 0),
                                "processing_time_ms": localization_result.get("elapsed_ms", 0)
                            }
                            
                            workflow_status = "completed"
                            success = True
                        else:
                            logger.warning("Localization failed via API call")
                            formatted_localization = None
                            workflow_status = "localization_failed"
                            success = False
                        
                        # Skip to step 5 since we already have the result
                        target_image_path = None
                
                # Process the image if we have a path
                if target_image_path:
                    localization_result = await self.rtabmap_service.process_image(target_image_path)
                    localization_elapsed = (time.time() - localization_start_time) * 1000
                    
                    if localization_result and localization_result.get("localization_successful"):
                        logger.info("Localization completed successfully")
                        
                        # CRITICAL: Extract GLOBAL coordinates from localization result
                        # rtabmap_service.process_image() returns GLOBAL coordinates directly
                        user_x = localization_result.get("x", 0)
                        user_y = localization_result.get("y", 0)
                        user_z = localization_result.get("z", 0)
                        
                        # Validate coordinates are realistic (not rotation matrix values)
                        logger.info(f"User position from localization: X={user_x:.3f}, Y={user_y:.3f}, Z={user_z:.3f}")
                        if abs(user_x) < 1.0 and abs(user_y) < 1.0 and abs(user_z) < 0.1:
                            logger.warning(f"⚠️ User coordinates look like rotation matrix values, not global! X={user_x}, Y={user_y}")
                        
                        # Format localization results for API response
                        formatted_localization = {
                            "position": {
                                "x": user_x,
                                "y": user_y,
                                "z": user_z
                            },
                            "orientation": {
                                "roll": localization_result.get("roll", 0),
                                "pitch": localization_result.get("pitch", 0),
                                "yaw": localization_result.get("yaw", 0)
                            },
                            "detected_objects": localization_result.get("objects", ""),
                            "picture_id": localization_result.get("pic_id", 0),
                            "processing_time_ms": localization_result.get("elapsed_ms", 0)
                        }
                        
                        workflow_status = "completed"
                        success = True
                        
                    else:
                        logger.warning("Localization failed or returned invalid results")
                        formatted_localization = None
                        localization_elapsed = (time.time() - localization_start_time) * 1000
                        workflow_status = "localization_failed"
                        success = False
                    
            except Exception as e:
                logger.error(f"Localization failed: {e}")
                formatted_localization = None
                localization_elapsed = (time.time() - localization_start_time) * 1000
                workflow_status = "localization_error"
                success = False
            
            # Step 5: Add navigation guidance if both search and localization succeeded
            navigation_guidance = None
            nearest_frame_id = None
            total_distance_to_target = None
            multiple_frames_found = len(formatted_search_results) > 1
            # route_details = None  # NEW: Route details with intermediate frames - COMMENTED OUT FOR WEBAPP ONLY
            
            if success and formatted_localization and formatted_search_results:
                try:
                    from navigation_guidance import add_navigation_guidance
                    
                    user_position = formatted_localization["position"]
                    user_yaw = formatted_localization["orientation"]["yaw"]
                    
                    navigation_data = add_navigation_guidance(
                        search_results=formatted_search_results,
                        user_position=user_position,
                        user_yaw=user_yaw,
                        object_name=object_name
                    )
                    
                    if navigation_data["navigation_guidance"]:
                        nav = navigation_data["navigation_guidance"]
                        navigation_guidance = {
                            "target_object": nav["target_object"],
                            "target_frame_id": nav["target_frame_id"],
                            "direction": nav["direction"],
                            "distance": nav["distance"],
                            "bearing": nav["bearing"],
                            "turn_instruction": nav["turn_instruction"],
                            "is_at_location": nav["is_at_location"],
                            "clock_position": nav.get("clock_position", 12),  # NEW: Clock-face position
                            "clock_instruction": nav.get("clock_instruction", "")  # NEW: Clock-face instruction
                        }
                        nearest_frame_id = nav["target_frame_id"]
                        total_distance_to_target = nav["distance"]
                        
                        # Update search results with distance information
                        formatted_search_results = navigation_data["all_frames_with_distances"]
                        
                        # NEW: Generate route details with intermediate frames - COMMENTED OUT FOR WEBAPP ONLY
                        """
                        try:
                            from test_frame_extraction import generate_route_details
                            
                            user_frame_id = formatted_localization["picture_id"]
                            target_frame_id = nearest_frame_id
                            target_location = navigation_data["nearest_frame"]["location"]
                            
                            logger.info(f"Generating route details from Frame {user_frame_id} to Frame {target_frame_id}")
                            
                            route_details = generate_route_details(
                                user_frame_id=user_frame_id,
                                target_frame_id=target_frame_id,
                                user_position=user_position,
                                target_position=target_location,
                                db_path=self.database_path,
                                num_intermediate_frames=5,  # Extract 5 intermediate frames
                                image_format="JPEG",
                                image_quality=75  # Balance of quality and file size
                            )
                            
                            # Log summary without Base64 images to keep terminal output clean
                            if route_details and route_details.get('frame_extraction_success'):
                                frames_summary = [
                                    f"Frame {f['frame_id']} @ {f['distance_from_start']:.1f}m (image: {len(f.get('image_base64', ''))//1024}KB)"
                                    for f in route_details.get('frames', [])
                                ]
                                logger.info(f"Route details: {route_details['total_frames']} frames, {route_details['route_distance']:.2f}m distance")
                                logger.info(f"Frames extracted: {', '.join(frames_summary)}")
                            else:
                                logger.info(f"Route details generated with status: {route_details.get('frame_extraction_success', False)}")
                            
                        except Exception as e:
                            logger.warning(f"Failed to generate route details: {e}")
                            # Don't fail the entire workflow if route generation fails
                            route_details = None
                        """
                        
                except Exception as e:
                    logger.warning(f"Failed to calculate navigation guidance: {e}")
                    # Don't fail the entire workflow if navigation calculation fails
            
            # Step 6: Calculate timing information
            total_elapsed = (time.time() - workflow_start_time) * 1000
            
            timing_info = None
            if include_timing:
                timing_info = {
                    "search_duration": round(search_elapsed, 1),
                    "localization_duration": round(localization_elapsed, 1),
                    "total_duration": round(total_elapsed, 1)
                }
            
            # Step 7: Return structured results with navigation guidance and route details
            return {
                "success": success,
                "search_results": formatted_search_results,
                "localization_results": formatted_localization,
                "navigation_guidance": navigation_guidance,
                # "route_details": route_details,  # NEW: Intermediate frames with images - COMMENTED OUT FOR WEBAPP ONLY
                "nearest_frame_id": nearest_frame_id,
                "total_distance_to_target": total_distance_to_target,
                "multiple_frames_found": multiple_frames_found,
                "total_matches": len(formatted_search_results),
                "workflow_status": workflow_status,
                "timing_ms": timing_info,
                "error_message": None if success else f"Workflow failed at {workflow_status} stage"
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            total_elapsed = (time.time() - workflow_start_time) * 1000
            
            return {
                "success": False,
                "search_results": [],
                "localization_results": None,
                "total_matches": 0,
                "workflow_status": "workflow_error",
                "timing_ms": {"total_duration": round(total_elapsed, 1)} if include_timing else None,
                "error_message": f"Workflow execution failed: {str(e)}"
            }
    
    def _is_running_in_container(self) -> bool:
        """
        Detect if we're running inside a Docker container.
        
        Returns:
            True if running in container, False if standalone
        """
        # Check for Docker-specific indicators
        try:
            # Method 1: Check if /.dockerenv file exists (most reliable)
            if os.path.exists("/.dockerenv"):
                return True
                
            # Method 2: Check if external test image directory exists (Docker volume mount)
            if os.path.exists("/external_testimage"):
                return True
                
            # Method 3: Check cgroup for Docker container indicators
            with open("/proc/1/cgroup", "r") as f:
                content = f.read()
                if "docker" in content.lower() or "container" in content.lower():
                    return True
                    
        except (FileNotFoundError, PermissionError):
            # These files don't exist on Windows or we don't have permission
            pass
        
        # If none of the Docker indicators are found, assume standalone
        return False
    
    async def _call_localization_api(self) -> Dict[str, Any]:
        """
        Call the /localize API endpoint as fallback when running outside container.
        
        Returns:
            Localization result dictionary
        """
        try:
            import aiohttp
            
            # Call the local API endpoint
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:8040/localize") as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        logger.error(f"API call failed with status {response.status}")
                        return {"localization_successful": False}
                        
        except Exception as e:
            logger.error(f"Failed to call localization API: {e}")
            return {"localization_successful": False}

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get status information about the workflow service and its dependencies.
        
        Returns:
            Dictionary with status information
        """
        try:
            database_exists = Path(self.database_path).exists()
            rtabmap_status = self.rtabmap_service.get_status() if self.rtabmap_service else None
            
            return {
                "workflow_service_ready": True,
                "database_path": self.database_path,
                "database_exists": database_exists,
                "rtabmap_service_status": rtabmap_status
            }
        except Exception as e:
            return {
                "workflow_service_ready": False,
                "error": str(e)
            }


class WorkflowServiceManager:
    """
    Manager class to handle WorkflowService lifecycle and provide singleton access.
    
    This ensures the same WorkflowService instance is used throughout the application.
    """
    
    _instance: Optional[WorkflowService] = None
    
    @classmethod
    def initialize(cls, rtabmap_service: RTABMapService, database_path: str, metadata_db_path: str) -> WorkflowService:
        """
        Initialize the workflow service manager with dependencies.
        
        Args:
            rtabmap_service: Initialized RTABMapService instance
            database_path: Path to the RTAB-Map database file
            metadata_db_path: Path to the metadata database file (containing ObjMeta table)
            
        Returns:
            WorkflowService instance
        """
        cls._instance = WorkflowService(rtabmap_service, database_path, metadata_db_path)
        logger.info("WorkflowService initialized successfully")
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> Optional[WorkflowService]:
        """
        Get the current WorkflowService instance.
        
        Returns:
            WorkflowService instance if initialized, None otherwise
        """
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset the workflow service instance."""
        cls._instance = None