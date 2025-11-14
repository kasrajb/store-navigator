#!/usr/bin/env python3
"""
Test script for RTAB-Map API Base64 image upload functionality
"""

import base64
import requests
import json
import sys
from pathlib import Path

# Configuration
API_URL = "http://localhost:8040/search-and-localize"
TEST_IMAGE_PATH = "./data/test_images/test.jpg"  # Update with your test image path
OBJECT_NAME = "door"  # Update with object to search for

def test_base64_upload():
    """Test Base64 image upload to RTAB-Map API"""
    
    print("=== RTAB-Map Base64 Image Test ===\n")
    
    # Check if test image exists
    image_path = Path(TEST_IMAGE_PATH)
    if not image_path.exists():
        print(f"❌ Test image not found at: {TEST_IMAGE_PATH}")
        print("Please update TEST_IMAGE_PATH in this script")
        sys.exit(1)
    
    print(f"✓ Found test image: {TEST_IMAGE_PATH}")
    
    # Read image and convert to Base64
    print("Converting image to Base64...")
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
    
    print(f"✓ Base64 conversion complete")
    print(f"  Image size: {len(image_bytes)} bytes")
    print(f"  Base64 length: {len(base64_string)} characters\n")
    
    # Test 1: Base64 string only
    print("Test 1: Sending Base64 image to API...")
    
    try:
        # Prepare form data
        form_data = {
            'object_name': (None, OBJECT_NAME),
            'image_base64': (None, base64_string),
            'include_timing': (None, 'true')
        }
        
        # Make API request
        response = requests.post(API_URL, files=form_data, timeout=30)
        
        if response.status_code == 200:
            print("✓ API call successful!\n")
            print("=== Response ===")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed!")
        print(f"Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_base64_upload()
