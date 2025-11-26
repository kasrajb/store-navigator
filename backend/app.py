import os
import time
import logging
import tempfile
import shutil
import base64
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import glob
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Import our custom modules
from rtabmap_service import RTABMapService

# Set logging to DEBUG to see detailed output
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.DEBUG)
logger = logging.getLogger("rtabmap_api")

# Initialize FastAPI app
app = FastAPI(
    title="RTAB-Map API",
    description="RTAB-Map localization API with integrated object search functionality",
    version="1.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global variables
rtabmap_service = None
workflow_service = None

# Define base data directories
DATA_DIR = Path("/data")
DB_FILE_PATH = DATA_DIR / "database.db"       # Embedded database
EXTERNAL_TESTIMAGE_DIR = Path("/external_testimage")  # External test image directory

# --- Pydantic Models for API Endpoints ---

class SearchLocalizeRequest(BaseModel):
    """Request model for the search-and-localize endpoint."""
    object_name: str = Field(..., description="Name of the object to search for", example="door")
    include_timing: bool = Field(default=True, description="Include timing information in response")

class SearchResult(BaseModel):
    """Model representing a single search result."""
    frame_id: int = Field(..., description="Database frame ID where object was found")
    location: Dict[str, float] = Field(..., description="X,Y coordinates of the frame", example={"x": 0.90, "y": 0.07})
    objects: List[str] = Field(..., description="List of matching objects with descriptions")

class LocalizationResult(BaseModel):
    """Model representing localization results."""
    position: Dict[str, float] = Field(..., description="3D position coordinates", example={"x": 0.9, "y": 0.07, "z": -0.04})
    orientation: Dict[str, float] = Field(..., description="Orientation angles in radians", example={"roll": 0.07, "pitch": -0.43, "yaw": 0.17})
    detected_objects: str = Field(..., description="String of detected objects in current scene")
    picture_id: int = Field(..., description="ID of the matched picture/frame")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")

class NavigationGuidance(BaseModel):
    """Model representing navigation guidance information."""
    target_object: str = Field(..., description="Name of the target object", example="orange door")
    target_frame_id: int = Field(..., description="Frame ID of the nearest target", example=45)
    
    # Clock-face guidance (NEW - primary system for blind users)
    clock_position: int = Field(..., description="Clock position (1-12) for orientation", example=2)
    clock_instruction: str = Field(..., description="Clock-face navigation instruction", example="Turn right to face 2 o'clock. Then walk approximately 2 meters.")
    
    # Legacy guidance (backward compatibility)
    direction: str = Field(..., description="Human-readable direction text (legacy)", example="ahead and to your right, approximately 2.3 meters away")
    turn_instruction: str = Field(..., description="Turn instruction for navigation (legacy)", example="Turn 35° to your right")
    
    # Common fields
    distance: float = Field(..., description="Distance to target in meters", example=2.3)
    bearing: float = Field(..., description="Relative bearing in degrees", example=35.2)
    is_at_location: bool = Field(..., description="Whether user is already at the target location")

class RouteFrame(BaseModel):
    """Model representing a single frame along the navigation route."""
    frame_id: int = Field(..., description="Frame ID from database", example=150)
    position: Dict[str, float] = Field(..., description="2D position coordinates in meters", example={"x": 4.5, "y": -12.3})
    distance_from_start: float = Field(..., description="Distance from user's starting position in meters", example=8.5)

# class RouteDetails(BaseModel):  # COMMENTED OUT FOR WEBAPP ONLY - N8N workflow integration
#     """Model representing complete route information with intermediate frames."""
#     total_frames: int = Field(..., description="Total number of frames in route", example=6)
#     route_distance: float = Field(..., description="Total distance from start to end in meters", example=18.5)
#     frame_extraction_success: bool = Field(..., description="Whether all frame images were extracted successfully")
#     frames: List[RouteFrame] = Field(..., description="Ordered list of frames from user location to target")
#     images: Optional[List[Optional[str]]] = Field(default=[], description="Simple array of Base64-encoded images (without metadata) for webapp processing")
#     error_message: Optional[str] = Field(None, description="Error message if frame extraction failed")

class SearchLocalizeResponse(BaseModel):
    """Response model for the search-and-localize endpoint."""
    success: bool = Field(..., description="Whether the workflow completed successfully")
    search_results: List[SearchResult] = Field(..., description="List of objects found matching the search term")
    localization_results: Optional[LocalizationResult] = Field(None, description="Localization data if successful")
    navigation_guidance: Optional[NavigationGuidance] = Field(None, description="Directional guidance to nearest object")
    # route_details: Optional[RouteDetails] = Field(None, description="Intermediate frames with images along the route for landmark-based navigation")  # COMMENTED OUT FOR WEBAPP ONLY
    nearest_frame_id: Optional[int] = Field(None, description="ID of the nearest frame selected for navigation")
    total_distance_to_target: Optional[float] = Field(None, description="Distance to the nearest target in meters")
    multiple_frames_found: bool = Field(default=False, description="Whether multiple frames contain the object")
    total_matches: int = Field(..., description="Total number of search matches found")
    workflow_status: str = Field(..., description="Status of workflow execution", example="completed")
    timing_ms: Optional[Dict[str, float]] = Field(None, description="Timing information for performance analysis")
    error_message: Optional[str] = Field(None, description="Error message if workflow failed")

def get_test_image_path():
    """
    Finds the first image file in the external test image directory.
    Supports common image formats: jpg, jpeg, png, bmp, tiff, tif
    """
    if not EXTERNAL_TESTIMAGE_DIR.exists():
        raise FileNotFoundError(f"External test image directory not found: {EXTERNAL_TESTIMAGE_DIR}")
    
    # Common image file extensions
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
    
    for pattern in image_extensions:
        image_files = list(EXTERNAL_TESTIMAGE_DIR.glob(pattern))
        image_files.extend(list(EXTERNAL_TESTIMAGE_DIR.glob(pattern.upper())))  # Check uppercase too
        
        if image_files:
            # Return the first image found
            selected_image = image_files[0]
            logger.info(f"Found test image: {selected_image}")
            return selected_image
    
    raise FileNotFoundError(f"No image files found in external directory: {EXTERNAL_TESTIMAGE_DIR}")

@app.on_event("startup")
async def startup_event():
    """
    Initialize the RTAB-Map service with the embedded database at startup.
    """
    global rtabmap_service, workflow_service
    logger.info("Starting RTAB-Map API service...")
    
    # Check if the embedded database exists
    if not DB_FILE_PATH.is_file():
        logger.error(f"Embedded database not found: {DB_FILE_PATH}")
        raise RuntimeError(f"Embedded database not found: {DB_FILE_PATH}")
    
    # Check if the external test image directory exists and contains an image
    try:
        test_image_path = get_test_image_path()
        logger.info(f"Using external test image: {test_image_path}")
    except FileNotFoundError as e:
        logger.warning(f"External test image directory not available: {e}. Localization endpoints will not work without mounted test images.")
        test_image_path = None
    
    # Initialize the RTAB-Map service once at startup
    rtabmap_service = RTABMapService()
    if not await rtabmap_service.initialize(DB_FILE_PATH):
        logger.error("Failed to initialize RTAB-Map service at startup")
        raise RuntimeError("Failed to initialize RTAB-Map service")
    
    # Initialize the workflow service for search-and-localize functionality
    try:
        from workflow_service import WorkflowServiceManager
        workflow_service = WorkflowServiceManager.initialize(rtabmap_service, str(DB_FILE_PATH))
        logger.info("WorkflowService initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize WorkflowService: {e}")
        raise RuntimeError(f"Failed to initialize WorkflowService: {e}")
    
    logger.info(f"RTAB-Map service initialized successfully with database: {DB_FILE_PATH}")
    logger.info(f"External test image directory: {EXTERNAL_TESTIMAGE_DIR}")
    logger.info("All services initialized - API ready for requests")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Properly shuts down the RTAB-Map service when the application is closing.
    """
    global workflow_service
    if rtabmap_service:
        await rtabmap_service.shutdown()
        logger.info("RTAB-Map service shut down successfully.")
    
    if workflow_service:
        from workflow_service import WorkflowServiceManager
        WorkflowServiceManager.reset()
        workflow_service = None
        logger.info("WorkflowService shut down successfully.")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/status")
async def service_status():
    """
    Returns detailed status information about the RTAB-Map service and workflow capabilities.
    """
    if not rtabmap_service:
        return {"status": "error", "message": "RTAB-Map service not created."}
        
    service_status = rtabmap_service.get_status()
    
    try:
        current_test_image = get_test_image_path()
        test_image_status = {"path": str(current_test_image), "exists": True}
    except FileNotFoundError as e:
        test_image_status = {"error": str(e), "exists": False}
    
    # Get workflow service status
    workflow_status = None
    if workflow_service:
        try:
            workflow_status = workflow_service.get_service_status()
        except Exception as e:
            workflow_status = {"error": f"Failed to get workflow status: {e}"}
    
    return {
        "status": "ok",
        "rtabmap_service": service_status,
        "workflow_service": workflow_status,
        "embedded_db": str(DB_FILE_PATH),
        "external_test_image": test_image_status,
        "external_directory": str(EXTERNAL_TESTIMAGE_DIR),
        "available_endpoints": ["/health", "/status", "/localize", "/search-and-localize"],
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """
    Simple health check to confirm the API is running.
    """
    return {
        "status": "ok",
        "service": "rtabmap-api",
        "version": "1.1",
        "features": ["localization", "search-and-localize", "object-search"],
        "timestamp": time.time()
    }

@app.post("/search-and-localize", response_model=SearchLocalizeResponse, tags=["Integrated Workflow"])
async def search_and_localize(
    object_name: str = Form(..., description="Name of the object to search for"),
    image: Optional[UploadFile] = File(None, description="Image file for localization (JPEG, PNG, BMP)"),
    image_base64: Optional[str] = Form(None, description="Base64-encoded image string (alternative to file upload)"),
    include_timing: bool = Form(default=True, description="Include timing information in response")
):
    """
    Integrated endpoint that searches for an object and performs localization with an uploaded image.
    
    This endpoint combines the functionality of product search with 
    RTAB-Map localization in a single automated workflow for webapp integration.
    
    **Workflow Steps:**
    1. Receive and validate uploaded image (file or Base64)
    2. Search for the specified object in the database
    3. Return matching locations with coordinates
    4. Perform localization using the uploaded image
    5. Calculate navigation guidance (distance, bearing, direction)
    6. Return current pose, detected objects, and navigation instructions
    
    **Use Cases:**
    - Webapp integration: Send captured images with object queries from mobile devices
    - Real-time navigation: Upload current view and get directions to target
    - Mobile object localization with dynamic images
    
    **Image Requirements:**
    - Format: JPEG, PNG, or BMP
    - Maximum size: 10 MB
    - Provide EITHER 'image' file OR 'image_base64' string (not both)
    
    **Base64 Format:**
    - Can include data URI prefix (e.g., "data:image/jpeg;base64,...")
    - Or raw Base64 string
    
    Returns:
        SearchLocalizeResponse with search results, localization data, and navigation guidance
    """
    temp_image_path = None
    cleanup_temp_file = False
    
    try:
        # Step 0: Validate input - either image file or Base64 string must be provided
        if not image and not image_base64:
            raise HTTPException(
                status_code=400, 
                detail="Either 'image' file or 'image_base64' string must be provided"
            )
        
        if image and image_base64:
            raise HTTPException(
                status_code=400, 
                detail="Provide either 'image' file OR 'image_base64', not both"
            )
        
        # Step 1: Validate workflow service is available
        if not workflow_service:
            raise HTTPException(
                status_code=503, 
                detail="Workflow service not available. Please check service initialization."
            )
        
        # Step 2: Handle Base64 image if provided
        if image_base64:
            logger.info("Processing Base64-encoded image")
            
            try:
                # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,")
                if "," in image_base64:
                    logger.debug("Removing data URI prefix from Base64 string")
                    image_base64 = image_base64.split(",", 1)[1]
                
                # Decode Base64 string to bytes
                image_bytes = base64.b64decode(image_base64)
                
                # Validate decoded size (10 MB limit)
                file_size_mb = len(image_bytes) / (1024 * 1024)
                if file_size_mb > 10:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Decoded image too large. Maximum size: 10 MB. Received: {file_size_mb:.2f} MB"
                    )
                
                logger.info(f"Base64 image decoded successfully: {file_size_mb:.2f} MB")
                
            except base64.binascii.Error as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid Base64 image data: {str(e)}"
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid Base64 format: {str(e)}"
                )
            
            # Create temporary file for Base64 image
            try:
                # Create temporary directory in /data/temp_uploads
                temp_dir = DATA_DIR / "temp_uploads"
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                # Create temporary file with .jpg extension
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".jpg",
                    dir=str(temp_dir),
                    prefix="base64_"
                )
                temp_image_path = Path(temp_file.name)
                
                # Write decoded bytes to file
                temp_file.write(image_bytes)
                temp_file.close()
                
                cleanup_temp_file = True
                logger.info(f"Base64 image saved to: {temp_image_path}")
                
            except Exception as e:
                logger.error(f"Failed to save Base64 image: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process Base64 image: {str(e)}"
                )
        
        # Step 3: Handle file upload if provided (existing logic)
        elif image:
            logger.info(f"Received image upload: {image.filename}, content_type: {image.content_type}")
            
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/bmp", "image/jpg"]
            if image.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image format. Allowed formats: JPEG, PNG, BMP. Received: {image.content_type}"
                )
            
            # Validate file size (10 MB limit)
            file_content = await image.read()
            file_size_mb = len(file_content) / (1024 * 1024)
            
            if file_size_mb > 10:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image file too large. Maximum size: 10 MB. Received: {file_size_mb:.2f} MB"
                )
            
            logger.info(f"Image validation passed: {file_size_mb:.2f} MB")
            
            # Save uploaded image to temporary file
            try:
                # Create a temporary file with the same extension as the uploaded file
                file_extension = Path(image.filename).suffix
                if not file_extension:
                    file_extension = ".jpg"  # Default to JPEG if no extension
                
                # Create temporary file in the /data directory (mounted volume)
                temp_dir = DATA_DIR / "temp_uploads"
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=file_extension,
                    dir=str(temp_dir),
                    prefix="upload_"
                )
                temp_image_path = Path(temp_file.name)
                
                # Write the image content to the temporary file
                temp_file.write(file_content)
                temp_file.close()
                
                cleanup_temp_file = True
                logger.info(f"Saved uploaded image to: {temp_image_path}")
                
            except Exception as e:
                logger.error(f"Failed to save uploaded image: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process uploaded image: {str(e)}"
                )
        
        # Step 4: Execute the integrated workflow with the uploaded image
        logger.info(f"Processing search-and-localize request for object: {object_name}")
        
        result = await workflow_service.execute_workflow(
            object_name=object_name,
            include_timing=include_timing,
            image_path=temp_image_path  # Pass the uploaded image path
        )
        
        # Log the workflow result for debugging
        logger.info(f"Workflow completed with status: {result.get('workflow_status')}")
        
        # Return the structured response
        return SearchLocalizeResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search-and-localize endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error during workflow execution: {str(e)}"
        )
    finally:
        # Step 5: Clean up temporary file
        if cleanup_temp_file and temp_image_path and temp_image_path.exists():
            try:
                temp_image_path.unlink()
                logger.debug(f"Cleaned up temporary image: {temp_image_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary image {temp_image_path}: {e}")

@app.post("/search", tags=["Search"])
async def search_only(request: SearchLocalizeRequest):
    """
    Search for objects in the RTAB-Map database without localization.
    
    This endpoint performs only the search functionality, returning
    matching frames and object locations without triggering localization.
    """
    try:
        # Import search functionality
        from search_product import search_products
        
        # Perform the search using the existing database path
        search_results = search_products(
            search_term=request.object_name,
            db_path=str(DB_FILE_PATH),
            use_sql_prefilter=True,
            show_performance=False
        )
        
        # Format results for API response
        formatted_results = []
        for result in search_results:
            formatted_result = {
                "frame_id": result['frame_id'],
                "location": {
                    "x": result['x'],
                    "y": result['y']
                },
                "objects": result['objects']
            }
            formatted_results.append(formatted_result)
        
        return {
            "success": True,
            "results": formatted_results,
            "total_matches": len(formatted_results),
            "search_term": request.object_name
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/localize", tags=["Localization"])
async def localize():
    """
    Localize the external test image against the embedded RTAB-Map database.
    Uses embedded database with external test image for optimal performance.
    
    This endpoint performs only localization without object search.
    For integrated search-and-localize functionality, use /search-and-localize endpoint.
    """
    start_time = time.time()
    
    try:
        # Ensure the service is initialized
        if not rtabmap_service or not rtabmap_service.is_initialized:
            raise HTTPException(status_code=500, detail="RTAB-Map service not initialized.")

        # Get the current test image from external directory
        try:
            test_image_path = get_test_image_path()
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # Process the external test image
        result = await rtabmap_service.process_image(test_image_path)

        if result:
            elapsed_time = time.time() - start_time
            result["elapsed_ms"] = round(elapsed_time * 1000, 1)
            result["external_image_processing"] = True
            logger.info(f"Processed external image in {elapsed_time*1000:.1f}ms: {result}")
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to process external image")
        
    except Exception as e:
        logger.exception(f"An error occurred during localization: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")
