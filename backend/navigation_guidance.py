"""
Navigation Guidance Module

This module provides proximity-based navigation and directional guidance functionality
for the RTAB-Map search and localization system. It calculates distances, selects
the nearest frame when multiple matches are found, and provides human-readable
navigation instructions.
"""

import math
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


def calculate_distance(pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
    """
    Calculate Euclidean distance between two 2D positions.
    
    Args:
        pos1: Dictionary with 'x' and 'y' keys
        pos2: Dictionary with 'x' and 'y' keys
        
    Returns:
        Distance in meters (or whatever unit the coordinates use)
    """
    dx = pos2['x'] - pos1['x']
    dy = pos2['y'] - pos1['y']
    return math.sqrt(dx**2 + dy**2)


def select_nearest_frame(user_position: Dict[str, float], 
                        search_results: List[Dict]) -> Tuple[Dict, List[Dict]]:
    """
    Select the nearest frame from search results based on user position.
    
    Args:
        user_position: Dict with 'x', 'y' keys (user's current position)
        search_results: List of search result dictionaries with 'location' key
        
    Returns:
        Tuple of (nearest_frame, all_frames_with_distances)
    """
    frames_with_distances = []
    
    for frame in search_results:
        distance = calculate_distance(user_position, frame['location'])
        frame_with_distance = frame.copy()
        frame_with_distance['distance_from_user'] = distance
        frames_with_distances.append(frame_with_distance)
    
    # Sort by distance
    frames_with_distances.sort(key=lambda f: f['distance_from_user'])
    
    nearest_frame = frames_with_distances[0]
    
    return nearest_frame, frames_with_distances


def calculate_direction(user_pos: Dict[str, float], 
                       target_pos: Dict[str, float],
                       user_yaw: float) -> Dict[str, Any]:
    """
    Calculate directional guidance from user position to target.
    
    Args:
        user_pos: Dict with 'x', 'y' keys (user's position)
        target_pos: Dict with 'x', 'y' keys (target position)
        user_yaw: User's orientation in radians (from localization)
        
    Returns:
        Dict with:
        - direction: String description (e.g., "ahead and to your left")
        - distance: Float distance in meters
        - bearing: Angle in degrees
        - turn_instruction: String (e.g., "Turn 30° left")
    """
    logger.info("="*80)
    logger.info("NAVIGATION CALCULATION DETAILS")
    logger.info("="*80)
    
    # Calculate vector from user to target
    dx = target_pos['x'] - user_pos['x']
    dy = target_pos['y'] - user_pos['y']
    
    # FIX: Invert Y-axis to correct RTAB-Map coordinate system
    # RTAB-Map: Moving forward/east → Y becomes MORE NEGATIVE
    # Navigation expects: Moving forward → Positive Y
    # Solution: Negate dy AND yaw before bearing calculation
    dy = -dy
    corrected_yaw = -user_yaw
    
    logger.info(f"User Position: x={user_pos['x']:.2f}, y={user_pos['y']:.2f}")
    logger.info(f"Target Position: x={target_pos['x']:.2f}, y={target_pos['y']:.2f}")
    logger.info(f"Vector Components: dx={dx:.2f}, dy={dy:.2f} (Y-axis inverted)")
    logger.info(f"User Yaw (orientation): {user_yaw:.4f} radians = {math.degrees(user_yaw):.1f}° (original)")
    logger.info(f"Corrected Yaw: {corrected_yaw:.4f} radians = {math.degrees(corrected_yaw):.1f}° (inverted)")
    
    # Calculate absolute bearing (angle from positive x-axis)
    target_bearing_rad = math.atan2(dy, dx)
    target_bearing_deg = math.degrees(target_bearing_rad)
    
    logger.info(f"Absolute Target Bearing: {target_bearing_rad:.4f} radians = {target_bearing_deg:.1f}°")
    
    # Calculate relative bearing (relative to user's current orientation)
    # Use corrected_yaw instead of user_yaw
    relative_bearing_rad = target_bearing_rad - corrected_yaw
    
    logger.info(f"Relative Bearing (before normalization): {relative_bearing_rad:.4f} radians = {math.degrees(relative_bearing_rad):.1f}°")
    
    # Normalize to [-pi, pi]
    while relative_bearing_rad > math.pi:
        relative_bearing_rad -= 2 * math.pi
    while relative_bearing_rad < -math.pi:
        relative_bearing_rad += 2 * math.pi
    
    # Convert to degrees
    relative_bearing_deg = math.degrees(relative_bearing_rad)
    
    logger.info(f"Relative Bearing (after normalization): {relative_bearing_rad:.4f} radians = {relative_bearing_deg:.1f}°")
    
    # Calculate distance
    distance = calculate_distance(user_pos, target_pos)
    
    logger.info(f"Distance to Target: {distance:.2f} meters")
    
    # Generate human-readable direction
    direction_text = generate_direction_text(relative_bearing_deg, distance)
    turn_instruction = generate_turn_instruction(relative_bearing_deg)
    
    logger.info(f"Generated Direction: {direction_text}")
    logger.info(f"Turn Instruction: {turn_instruction}")
    logger.info("="*80)
    
    return {
        'direction': direction_text,
        'distance': round(distance, 2),
        'bearing': round(relative_bearing_deg, 1),
        'turn_instruction': turn_instruction
    }


def generate_direction_text(bearing_deg: float, distance: float) -> str:
    """
    Generate natural, accessible direction text for blind/visually impaired users.
    Uses intuitive phrasing that's easy to speak and understand.
    """
    
    # Determine direction (8-point compass)
    if -22.5 <= bearing_deg <= 22.5:
        direction = "straight ahead"
    elif 22.5 < bearing_deg <= 67.5:
        direction = "ahead and to your right"
    elif 67.5 < bearing_deg <= 112.5:
        direction = "on your right"
    elif 112.5 < bearing_deg <= 157.5:
        direction = "behind you on the right"
    elif bearing_deg > 157.5 or bearing_deg < -157.5:
        direction = "directly behind you"
    elif -157.5 <= bearing_deg < -112.5:
        direction = "behind you on the left"
    elif -112.5 <= bearing_deg < -67.5:
        direction = "on your left"
    elif -67.5 <= bearing_deg < -22.5:
        direction = "ahead and to your left"
    
    # Generate natural distance descriptions
    if distance < 0.3:
        # Very close - emphasize immediacy
        return f"Right {direction}"
    
    elif distance < 1.0:
        # Close - use simple integer
        distance_int = round(distance)
        if distance_int == 0:
            distance_int = 1  # Avoid saying "zero meters"
        return f"About {distance_int} meter {direction}"
    
    elif distance < 3.0:
        # Medium distance - round to nearest 0.5
        distance_rounded = round(distance * 2) / 2
        return f"{direction.capitalize()}, about {distance_rounded} meters"
    
    elif distance < 10.0:
        # Longer distance - round to integer
        distance_int = round(distance)
        return f"{direction.capitalize()}, roughly {distance_int} meters"
    
    else:
        # Very far - round to nearest 5 meters
        distance_rounded = round(distance / 5) * 5
        return f"{direction.capitalize()}, approximately {distance_rounded} meters away"


def generate_turn_instruction(bearing_deg: float) -> str:
    """
    Generate natural turn instruction for blind/visually impaired users.
    Avoids precise degree measurements, uses intuitive descriptions.
    """
    abs_bearing = abs(bearing_deg)
    
    # Very small angle - essentially straight
    if abs_bearing < 15:
        return "Keep going straight"
    
    # Slight turn (15-45 degrees)
    elif abs_bearing < 45:
        if bearing_deg > 0:
            return "Turn slightly to your right"
        else:
            return "Turn slightly to your left"
    
    # Moderate turn (45-90 degrees)
    elif abs_bearing < 90:
        if bearing_deg > 0:
            return "Make a right turn"
        else:
            return "Make a left turn"
    
    # Sharp turn (90-135 degrees)
    elif abs_bearing < 135:
        if bearing_deg > 0:
            return "Turn sharply to your right"
        else:
            return "Turn sharply to your left"
    
    # U-turn or nearly behind (135-180 degrees)
    else:
        return "Turn around"


def add_navigation_guidance(search_results: List[Dict], 
                           user_position: Dict[str, float],
                           user_yaw: float,
                           object_name: str) -> Dict[str, Any]:
    """
    Add navigation guidance to search results.
    
    Args:
        search_results: List of search results from product search
        user_position: User's current position from localization  
        user_yaw: User's current orientation in radians
        object_name: Name of the object being searched for
        
    Returns:
        Dictionary containing:
        - nearest_frame: The closest frame to navigate to
        - all_frames_with_distances: All frames with distance information
        - navigation_guidance: Directional guidance to nearest frame
        - multiple_frames_message: Message to display if multiple frames found
    """
    if not search_results:
        return {
            'nearest_frame': None,
            'all_frames_with_distances': [],
            'navigation_guidance': None,
            'multiple_frames_message': None
        }
    
    logger.info(f"Starting navigation guidance calculation for '{object_name}'")
    logger.info(f"User position: {user_position}, User yaw: {user_yaw:.4f} rad")
    logger.info(f"Number of search results: {len(search_results)}")
    
    # Calculate distances and select nearest frame
    nearest_frame, all_frames = select_nearest_frame(user_position, search_results)
    
    logger.info(f"Nearest frame selected: Frame {nearest_frame['frame_id']} at location {nearest_frame['location']}")
    
    # Generate multiple frames message if applicable
    multiple_frames_message = None
    if len(search_results) > 1:
        multiple_frames_message = "⚠️  The object exists in several frames. I will guide you to the nearest frame."
    
    # Calculate navigation guidance to nearest frame
    navigation_guidance = calculate_direction(
        user_pos=user_position,
        target_pos=nearest_frame['location'],
        user_yaw=user_yaw
    )
    
    # Add object name and frame info
    navigation_guidance['target_object'] = object_name
    navigation_guidance['target_frame_id'] = nearest_frame['frame_id']
    navigation_guidance['is_at_location'] = navigation_guidance['distance'] < 0.3
    
    logger.info("="*80)
    logger.info("FINAL NAVIGATION GUIDANCE")
    logger.info("="*80)
    logger.info(f"Target Object: {navigation_guidance['target_object']}")
    logger.info(f"Target Frame ID: {navigation_guidance['target_frame_id']}")
    logger.info(f"Direction: {navigation_guidance['direction']}")
    logger.info(f"Turn Instruction: {navigation_guidance['turn_instruction']}")
    logger.info(f"Distance: {navigation_guidance['distance']} meters")
    logger.info(f"Bearing: {navigation_guidance['bearing']}°")
    logger.info(f"At Location: {navigation_guidance['is_at_location']}")
    logger.info("="*80)
    
    return {
        'nearest_frame': nearest_frame,
        'all_frames_with_distances': all_frames,
        'navigation_guidance': navigation_guidance,
        'multiple_frames_message': multiple_frames_message
    }


def format_navigation_display(navigation_data: Dict[str, Any]) -> str:
    """
    Format navigation guidance for CLI display.
    
    Args:
        navigation_data: Navigation data from add_navigation_guidance()
        
    Returns:
        Formatted string for terminal display
    """
    if not navigation_data['navigation_guidance']:
        return ""
    
    nav = navigation_data['navigation_guidance']
    
    output = "\n--- Navigation Guidance ---\n"
    output += f"🎯 Target: {nav['target_object']} (Frame {nav['target_frame_id']})\n"
    output += f"📍 Direction: {nav['direction']}\n"
    output += f"🧭 Turn Instruction: {nav['turn_instruction']}\n"
    output += f"📏 Distance: {nav['distance']} meters\n"
    
    if nav['is_at_location']:
        output += "\nYou are already at the object location!\n"
    
    return output


def format_search_results_with_distances(all_frames: List[Dict], 
                                        nearest_frame: Dict,
                                        multiple_frames_message: Optional[str] = None) -> str:
    """
    Format search results with distance information for CLI display.
    
    Args:
        all_frames: All frames with distance information
        nearest_frame: The nearest frame (for highlighting)
        multiple_frames_message: Message to show if multiple frames exist
        
    Returns:
        Formatted string for terminal display
    """
    output = "--- Search Results ---\n"
    output += f"Found {len(all_frames)} matches:\n\n"
    
    if multiple_frames_message:
        output += f"{multiple_frames_message}\n\n"
    
    for i, frame in enumerate(all_frames, 1):
        nearest_marker = " ⭐ NEAREST FRAME" if frame == nearest_frame else ""
        distance_text = f" ({frame['distance_from_user']:.2f}m away)"
        
        output += f"{i}. Frame {frame['frame_id']}{nearest_marker}{distance_text}\n"
        output += f"   Location: x={frame['location']['x']:.2f}, y={frame['location']['y']:.2f}\n"
        
        # Display matching objects
        if frame.get('objects'):
            # Show up to 3 most relevant objects
            display_objects = frame['objects'][:3]
            for obj in display_objects:
                output += f"   → {obj}\n"
            
            # Indicate if there are more objects
            if len(frame['objects']) > 3:
                output += f"   ... and {len(frame['objects']) - 3} more\n"
        
        output += "\n"  # Empty line between results
    
    return output