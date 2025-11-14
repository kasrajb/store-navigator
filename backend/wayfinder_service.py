"""
Wayfinder Service Module

This module handles all Wayfinder integration including:
- Coordinate system transformation from RTAB-Map to Wayfinder
- Communication with Wayfinder API
- Coordinate conversion utilities
"""

import math
import logging
import httpx
from typing import Dict

# Set up logging
logger = logging.getLogger("wayfinder")

# --- Wayfinder Integration Configuration ---
WAYFINDER_URL = "https://jennet-crisp-molly.ngrok-free.app/wayfinder"

# --- Coordinate System Transformation ---

# 1. Define reference points in RTAB-Map
# These are the known real-world coordinates within the RTAB-Map's coordinate system.
PROF_ROOM_SYS1 = {"x": 5.088, "y": 1.850}
LAB_ROOM_SYS1 = {"x": 0.227, "y": 13.160}

# 2. Define corresponding reference points in Wayfinder system
# These are the coordinates in the target system that match the points from RTAB-Map.
PROF_ROOM_SYS2 = {"x": 73.60, "y": 23.71}
LAB_ROOM_SYS2 = {"x": 62.59, "y": 15.14}

# 3. Calculate the transformation parameters (rotation and translation)
# This is done once on startup to be used for all subsequent transformations.

# Calculate the vector between the two reference points in RTAB-Map
v1 = (LAB_ROOM_SYS1["x"] - PROF_ROOM_SYS1["x"], LAB_ROOM_SYS1["y"] - PROF_ROOM_SYS1["y"])
# Calculate the vector between the two reference points in Wayfinder system
v2 = (LAB_ROOM_SYS2["x"] - PROF_ROOM_SYS2["x"], LAB_ROOM_SYS2["y"] - PROF_ROOM_SYS2["y"])

# Calculate the rotation angle (theta) required to align v1 with v2.
# The angle is the difference between the angles of the two vectors.
theta = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])

# Pre-calculate the cosine and sine of the rotation angle for efficiency.
cos_theta = math.cos(theta)
sin_theta = math.sin(theta)

# Calculate the translation (shift) needed after rotation.
# 1. Rotate a point from RTAB-Map.
prof_room_sys1_rotated_x = PROF_ROOM_SYS1["x"] * cos_theta - PROF_ROOM_SYS1["y"] * sin_theta
prof_room_sys1_rotated_y = PROF_ROOM_SYS1["x"] * sin_theta + PROF_ROOM_SYS1["y"] * cos_theta

# 2. Find the difference between the rotated RTAB-Map point and the target Wayfinder system point.
shift_x = PROF_ROOM_SYS2["x"] - prof_room_sys1_rotated_x
shift_y = PROF_ROOM_SYS2["y"] - prof_room_sys1_rotated_y


def transform_coordinates(x1: float, y1: float) -> Dict[str, float]:
    """
    Transforms coordinates from RTAB-Map to Wayfinder system.
    Applies a calculated rotation and translation.
    
    Args:
        x1: X coordinate in RTAB-Map system
        y1: Y coordinate in RTAB-Map system
        
    Returns:
        Dictionary with transformed x and y coordinates
    """
    # Step 1: Apply the rotation to the input coordinates.
    x_rotated = x1 * cos_theta - y1 * sin_theta
    y_rotated = x1 * sin_theta + y1 * cos_theta
    
    # Step 2: Apply the translation to the rotated coordinates.
    x2 = x_rotated + shift_x
    y2 = y_rotated + shift_y
    
    return {"x": round(x2, 2), "y": round(y2, 2)}


async def send_to_wayfinder(x: float, y: float) -> Dict:
    """
    Sends the user's current X and Y coordinates to the wayfinder API.
    
    Args:
        x: X coordinate in Wayfinder system
        y: Y coordinate in Wayfinder system
        
    Returns:
        Dictionary with API response or error information
    """
    payload = {
        "action": "update",
        "currentX": x,
        "currentY": y
    }
    
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Sending to wayfinder: {payload}")
            response = await client.post(WAYFINDER_URL, json=payload)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            logger.info(f"Successfully sent coordinates to wayfinder. Response: {response.json()}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error sending coordinates to wayfinder: {e}")
        return {"error": str(e)}


class WayfinderService:
    """
    Service class for managing Wayfinder integration.
    Provides methods for coordinate transformation and API communication.
    """
    
    @staticmethod
    def transform_rtabmap_to_wayfinder(x: float, y: float) -> Dict[str, float]:
        """
        Transform coordinates from RTAB-Map to Wayfinder coordinate system.
        
        Args:
            x: X coordinate in RTAB-Map system
            y: Y coordinate in RTAB-Map system
            
        Returns:
            Dictionary with transformed coordinates
        """
        return transform_coordinates(x, y)
    
    @staticmethod
    async def update_wayfinder_location(x: float, y: float) -> Dict:
        """
        Send location update to Wayfinder API.
        
        Args:
            x: X coordinate in Wayfinder system
            y: Y coordinate in Wayfinder system
            
        Returns:
            Dictionary with API response
        """
        return await send_to_wayfinder(x, y)
    
    @staticmethod
    async def process_localization_result(localization_result: Dict) -> Dict:
        """
        Process localization result: transform coordinates and update Wayfinder.
        
        Args:
            localization_result: Result from RTAB-Map localization
            
        Returns:
            Updated localization result with Wayfinder response
        """
        if localization_result and localization_result.get("localization_successful"):
            # Transform coordinates
            transformed_coords = transform_coordinates(
                localization_result["x"], 
                localization_result["y"]
            )
            
            # Send to Wayfinder
            wayfinder_response = await send_to_wayfinder(
                transformed_coords["x"], 
                transformed_coords["y"]
            )
            
            # Add Wayfinder response to result
            localization_result["wayfinder_update"] = wayfinder_response
            localization_result["transformed_coordinates"] = transformed_coords
            
        return localization_result
