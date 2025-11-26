#!/usr/bin/env python3
"""
RTAB-Map Object Search & Localization Integration Script

This script combines object search functionality with RTAB-Map localization API
in a seamless, automatic workflow. It searches for products using the existing
search_product.py functionality, displays results, and automatically triggers
localization without user confirmation.

Requirements:
- Docker container must be running on port 8040
- Existing search_product.py functionality available
- RTAB-Map database accessible

Usage:
    python integrated_search_localize.py
    python integrated_search_localize.py --help
    python integrated_search_localize.py --debug
"""

import sys
import time
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# Import workflow functionality
try:
    from workflow_service import WorkflowService
    from rtabmap_service import RTABMapService
except ImportError as e:
    print(f"Error: Could not import workflow functionality: {e}")
    print("Please ensure workflow_service.py and rtabmap_service.py are available.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("integrated_search_localize")

# Configuration
API_BASE_URL = "http://localhost:8040"
DATABASE_PATH = r"C:\Users\kasra\Desktop\Kasra\Telegram\Fall 2025\ECSE 542 Final Report\store-navigator\backend\data\database\IGA-V2.db"
REQUEST_TIMEOUT = 30  # seconds


class RTABMapIntegratedClient:
    """
    Integrated client that combines product search with RTAB-Map localization.
    
    This class now uses the shared WorkflowService to ensure identical behavior
    between CLI and API interfaces.
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize the integrated client.
        
        Args:
            debug: Enable debug logging if True
        """
        self.debug = debug
        self.workflow_service = None
        self.rtabmap_service = None
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
    
    async def initialize_services(self) -> bool:
        """
        Initialize the RTAB-Map and workflow services for CLI usage.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Check database exists first
            if not self.check_database_exists():
                return False
            
            # Initialize RTAB-Map service
            self.rtabmap_service = RTABMapService()
            if not await self.rtabmap_service.initialize(Path(DATABASE_PATH)):
                logger.error("Failed to initialize RTAB-Map service")
                return False
            
            # Initialize workflow service
            self.workflow_service = WorkflowService(self.rtabmap_service, DATABASE_PATH)
            logger.info("Services initialized successfully for CLI usage")
            return True
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return False
    
    def check_api_health(self) -> bool:
        """
        Check if the RTAB-Map API is accessible and healthy.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            logger.info("Checking API health...")
            response = requests.get(
                f"{API_BASE_URL}/health",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"API is healthy: {health_data.get('service', 'Unknown')} v{health_data.get('version', 'Unknown')}")
                return True
            else:
                logger.error(f"API health check failed with status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to RTAB-Map API. Is the Docker container running?")
            logger.error(f"Expected URL: {API_BASE_URL}")
            return False
        except requests.exceptions.Timeout:
            logger.error(f"API health check timed out after {REQUEST_TIMEOUT} seconds")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during health check: {e}")
            return False
    
    def check_database_exists(self) -> bool:
        """
        Check if the RTAB-Map database file exists.
        
        Returns:
            True if database exists, False otherwise
        """
        db_path = Path(DATABASE_PATH)
        if db_path.exists():
            logger.debug(f"Database found at: {DATABASE_PATH}")
            return True
        else:
            logger.error(f"Database not found at: {DATABASE_PATH}")
            return False
    
    async def execute_workflow_with_cli_output(self, search_term: str) -> bool:
        """
        Execute the workflow step by step, showing search results immediately, then localization.
        
        Args:
            search_term: Product name or description to search for
            
        Returns:
            True if workflow completed successfully, False otherwise
        """
        try:
            if not self.workflow_service:
                logger.error("Workflow service not initialized")
                return False
            
            print(f"\nSearching for \"{search_term}\"...\n")
            
            # Step 1: Do search first and show results immediately
            logger.info(f"Starting product search for: {search_term}")
            
            from search_product import search_products
            search_results = search_products(
                search_term=search_term,
                db_path=DATABASE_PATH,
                use_sql_prefilter=True,
                show_performance=False
            )
            
            logger.info(f"Product search completed: {len(search_results)} matches found")
            
            # Step 2: Now do localization to get user position
            print("Triggering localization...")
            logger.info("Starting automatic localization...")
            
            # Use the workflow service for complete workflow (to get user position)
            result = await self.workflow_service.execute_workflow(
                object_name=search_term,
                include_timing=self.debug
            )
            
            # Step 3: Add navigation guidance using localization results
            if result.get("success") and result.get("localization_results"):
                localization_results = result["localization_results"]
                user_position = localization_results["position"]  # x, y, z
                user_yaw = localization_results["orientation"]["yaw"]  # radians
                
                # Convert search results to format expected by navigation
                formatted_search_results = []
                for search_result in search_results:
                    formatted_result = {
                        "frame_id": search_result['frame_id'],
                        "location": {"x": search_result['x'], "y": search_result['y']},
                        "objects": search_result['objects']
                    }
                    formatted_search_results.append(formatted_result)
                
                # Get navigation guidance
                from navigation_guidance import add_navigation_guidance, format_search_results_with_distances, format_navigation_display
                
                navigation_data = add_navigation_guidance(
                    search_results=formatted_search_results,
                    user_position=user_position,
                    user_yaw=user_yaw,
                    object_name=search_term
                )
                
                # Display enhanced search results with distances
                print(format_search_results_with_distances(
                    all_frames=navigation_data['all_frames_with_distances'],
                    nearest_frame=navigation_data['nearest_frame'],
                    multiple_frames_message=navigation_data['multiple_frames_message']
                ))
                
                # Display localization results
                self.format_localization_results_from_workflow(result)
                
                # Display navigation guidance
                print(format_navigation_display(navigation_data))
                
            else:
                # Fallback: display original search results if localization failed
                self.display_search_results(search_results)
                self.format_localization_results_from_workflow(result)
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return False
    
    def display_search_results(self, search_results: List) -> None:
        """
        Display search results immediately when found.
        
        Args:
            search_results: List of search results from search_product
        """
        if not search_results:
            print("--- Search Results ---")
            print("No products found matching your search.")
            print()
        else:
            print("--- Search Results ---")
            print(f"Found {len(search_results)} matches:\n")
            
            for i, result in enumerate(search_results, 1):
                frame_id = result['frame_id']
                x = result['x']
                y = result['y']
                objects = result['objects']
                
                print(f"{i}. Frame {frame_id}")
                print(f"   Location: x={x:.2f}, y={y:.2f}")
                
                # Display matching objects
                if objects:
                    # Show up to 3 most relevant objects
                    display_objects = objects[:3]
                    for obj in display_objects:
                        print(f"   → {obj}")
                    
                    # Indicate if there are more objects
                    if len(objects) > 3:
                        print(f"   ... and {len(objects) - 3} more")
                
                print()  # Empty line between results
    

    def format_localization_results_from_workflow(self, workflow_result: Dict) -> None:
        """
        Display localization results from workflow in a formatted way for the terminal.
        
        Args:
            workflow_result: Complete workflow result from WorkflowService
        """
        print("--- Localization Results ---")
        
        if not workflow_result.get('success', False):
            error_msg = workflow_result.get('error_message', 'Unknown error occurred')
            print(f"Localization Error: {error_msg}")
            return
        
        localization_results = workflow_result.get('localization_results')
        if not localization_results:
            print("Localization Failed: Unable to determine position")
            return
        
        # Display position and orientation
        position = localization_results.get('position', {})
        orientation = localization_results.get('orientation', {})
        
        x = position.get('x', 0)
        y = position.get('y', 0)
        z = position.get('z', 0)
        roll = orientation.get('roll', 0)
        pitch = orientation.get('pitch', 0)
        yaw = orientation.get('yaw', 0)
        
        print(f"Position: x={x}, y={y}, z={z}")
        print(f"Orientation: roll={roll:.2f}, pitch={pitch:.2f}, yaw={yaw:.2f}")
        
        # Display detected objects
        objects = localization_results.get('detected_objects', '')
        if objects:
            print(f"Detected Objects: {objects}")
        else:
            print("Detected Objects: None")
        
        # Display picture ID and processing time
        pic_id = localization_results.get('picture_id')
        if pic_id is not None:
            print(f"Picture ID: {pic_id}")
        
        # Show processing time
        processing_time = localization_results.get('processing_time_ms')
        if processing_time is not None:
            print(f"Processing Time: {processing_time}ms")
        
        # Show timing breakdown if available
        timing_info = workflow_result.get('timing_ms')
        if timing_info and self.debug:
            print(f"Search Duration: {timing_info.get('search_duration', 0):.1f}ms")
            print(f"Localization Duration: {timing_info.get('localization_duration', 0):.1f}ms")
            print(f"Total Duration: {timing_info.get('total_duration', 0):.1f}ms")
    
    async def run_integrated_workflow(self, search_term: str) -> bool:
        """
        Run the complete integrated workflow using the shared WorkflowService.
        
        This method now uses the same business logic as the API endpoint,
        ensuring identical behavior between CLI and API interfaces.
        
        Args:
            search_term: Product to search for
            
        Returns:
            True if workflow completed successfully, False if any step failed
        """
        try:
            # Step 1: Initialize services (CLI mode)
            logger.debug("Starting integrated workflow...")
            
            if not await self.initialize_services():
                print("Error: Failed to initialize RTAB-Map services.")
                print("Please check that the database file exists and is accessible.")
                return False
            
            # Step 2: Execute the complete workflow using WorkflowService
            success = await self.execute_workflow_with_cli_output(search_term)
            
            if success:
                print("\n=== Workflow Complete ===")
            else:
                print("\n=== Workflow Failed ===")
                print("Check the error messages above for details.")
            
            return success
                
        except KeyboardInterrupt:
            print("\n\nWorkflow interrupted by user.")
            logger.info("Workflow interrupted by user (Ctrl+C)")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in workflow: {e}")
            print(f"\n=== Workflow Failed ===\nUnexpected error: {e}")
            return False


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Set up command line argument parsing.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="RTAB-Map Object Search & Localization Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python integrated_search_localize.py
  python integrated_search_localize.py --debug

The script will:
1. Prompt for an object name
2. Search for the object in the RTAB-Map database
3. Display search results
4. Automatically trigger localization (no confirmation required)
5. Display localization results

Prerequisites:
- Docker container running on port 8040
- RTAB-Map database available at the configured path
        """
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging and verbose output"
    )
    
    parser.add_argument(
        "--object",
        type=str,
        help="Object name to search for (skips interactive prompt)"
    )
    
    return parser


async def main():
    """
    Main entry point for the integrated search and localization script.
    """
    # Parse command line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Display welcome message
    print("=== RTAB-Map Object Search & Localization System ===")
    print()
    
    # Initialize the integrated client
    client = RTABMapIntegratedClient(debug=args.debug)
    
    # Get search term from command line or user input
    if args.object:
        search_term = args.object
        print(f"Searching for object: {search_term}")
    else:
        try:
            search_term = input("Enter the object you want to search for: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")
            return
    
    if not search_term:
        print("Please enter a search term.")
        return
    
    # Run the integrated workflow
    success = await client.run_integrated_workflow(search_term)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())