"""
Vision Pipeline Integration Example

This script demonstrates how to integrate the vision pipeline with the RTAB-Map API
to send images and object queries, then receive navigation guidance.

Usage:
    python vision_integration_example.py <image_path> <object_name>

Example:
    python vision_integration_example.py captured_scene.jpg "orange door"
"""

import sys
import requests
import json
from pathlib import Path


def call_rtabmap_api(image_path: str, object_name: str, api_url: str = "http://localhost:8040"):
    """
    Call the RTAB-Map API with an uploaded image and object query.
    
    Args:
        image_path: Path to the image file to upload
        object_name: Name of the object to search for
        api_url: Base URL of the RTAB-Map API
        
    Returns:
        Dictionary containing the API response with navigation guidance
    """
    # Validate image file exists
    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Prepare the request
    endpoint = f"{api_url}/search-and-localize"
    
    # Open the image file and send as multipart/form-data
    with open(image_file, 'rb') as img:
        files = {
            'image': (image_file.name, img, 'image/jpeg')
        }
        data = {
            'object_name': object_name,
            'include_timing': True
        }
        
        print(f"Sending request to: {endpoint}")
        print(f"Image: {image_file.name}")
        print(f"Object: {object_name}")
        print("-" * 60)
        
        # Send POST request
        response = requests.post(endpoint, files=files, data=data, timeout=30)
    
    # Check response status
    if response.status_code != 200:
        print(f"API Error (Status {response.status_code}): {response.text}")
        return None
    
    return response.json()


def display_results(result: dict):
    """
    Display the navigation guidance results in a human-readable format.
    
    Args:
        result: Dictionary containing the API response
    """
    if not result:
        print("No results to display")
        return
    
    print("\n" + "=" * 60)
    print("RTAB-MAP API RESPONSE")
    print("=" * 60)
    
    # Display search results
    print(f"\n[SEARCH RESULTS]")
    print(f"Success: {result['success']}")
    print(f"Total Matches: {result['total_matches']}")
    
    if result['search_results']:
        print(f"\nFound {len(result['search_results'])} location(s):")
        for i, location in enumerate(result['search_results'], 1):
            print(f"  {i}. Frame ID {location['frame_id']}: ({location['location']['x']:.2f}, {location['location']['y']:.2f})")
            if 'distance_from_user' in location:
                print(f"     Distance: {location['distance_from_user']:.2f}m")
    
    # Display localization results
    if result['localization_results']:
        loc = result['localization_results']
        print(f"\n[LOCALIZATION RESULTS]")
        print(f"Current Position: ({loc['position']['x']:.2f}, {loc['position']['y']:.2f}, {loc['position']['z']:.2f})")
        print(f"Current Orientation: Roll={loc['orientation']['roll']:.2f}, Pitch={loc['orientation']['pitch']:.2f}, Yaw={loc['orientation']['yaw']:.2f}")
        print(f"Matched Picture ID: {loc['picture_id']}")
        print(f"Processing Time: {loc['processing_time_ms']:.1f}ms")
        
        if loc['detected_objects']:
            print(f"Detected Objects: {loc['detected_objects']}")
    
    # Display navigation guidance - THIS IS THE KEY OUTPUT FOR THE VISION PIPELINE
    if result['navigation_guidance']:
        nav = result['navigation_guidance']
        print(f"\n[NAVIGATION GUIDANCE]")
        print(f"Target Object: {nav['target_object']}")
        print(f"Target Frame ID: {nav['target_frame_id']}")
        print(f"Direction: {nav['direction']}")
        print(f"Distance: {nav['distance']:.2f} meters")
        print(f"Bearing: {nav['bearing']:.1f} degrees")
        print(f"Turn Instruction: {nav['turn_instruction']}")
        print(f"At Location: {nav['is_at_location']}")
        
        # This is what your vision pipeline should use:
        print(f"\n>>> VISION PIPELINE OUTPUTS <<<")
        print(f"direction = \"{nav['direction']}\"")
        print(f"distance = {nav['distance']:.2f}  # meters")
        print(f"bearing = {nav['bearing']:.1f}  # degrees")
        print(f"turn_instruction = \"{nav['turn_instruction']}\"")
        print(f"is_at_location = {nav['is_at_location']}")
    
    # Display timing information
    if result['timing_ms']:
        timing = result['timing_ms']
        print(f"\n[TIMING INFORMATION]")
        print(f"Search Duration: {timing['search_duration']:.1f}ms")
        print(f"Localization Duration: {timing['localization_duration']:.1f}ms")
        print(f"Total Duration: {timing['total_duration']:.1f}ms")
    
    print("\n" + "=" * 60)


def main():
    """Main function to run the vision integration example."""
    if len(sys.argv) != 3:
        print("Usage: python vision_integration_example.py <image_path> <object_name>")
        print('Example: python vision_integration_example.py captured_scene.jpg "orange door"')
        sys.exit(1)
    
    image_path = sys.argv[1]
    object_name = sys.argv[2]
    
    try:
        # Call the API
        result = call_rtabmap_api(image_path, object_name)
        
        # Display the results
        display_results(result)
        
        # Return navigation guidance for programmatic use
        if result and result.get('navigation_guidance'):
            nav = result['navigation_guidance']
            return {
                'direction': nav['direction'],
                'distance': nav['distance'],
                'bearing': nav['bearing'],
                'turn_instruction': nav['turn_instruction'],
                'is_at_location': nav['is_at_location']
            }
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
