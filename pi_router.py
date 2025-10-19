#!/usr/bin/env python3
"""
Raspberry Pi Router/Gateway for HINT System
Simulates the HINT Gateway - pulls location data from Firebase every 5 seconds
and sends navigation commands back to the laptop client
"""

import time
import threading
import sys
from typing import Optional, Tuple
from firebase_client import FirebaseClient
from firebase_config import MessageTypes
from text_maps import TextMaps
from TTS import say

class PiRouter:
    """Raspberry Pi Router/Gateway for HINT system"""
    
    def __init__(self):
        """Initialize the Pi Router"""
        self.firebase = FirebaseClient()
        self.navigator = TextMaps()
        self.is_running = False
        self.current_destination = None
        self.current_route = None
        self.current_step = 0
        self.last_location = None
        self.update_interval = 5  # Pull location every 5 seconds
        
        print("🌐 HINT Gateway (Pi Router) Initialized")
        print("=" * 50)
    
    def start_router(self) -> bool:
        """
        Start the Pi Router service
        
        Returns:
            bool: True if started successfully
        """
        if not self.firebase.is_ready():
            print("❌ Firebase not ready. Please check configuration.")
            return False
        
        print("🚀 Starting HINT Gateway Router...")
        
        # Send initial status
        self.firebase.send_status_update("router", "starting", {
            "update_interval": self.update_interval,
            "capabilities": ["navigation", "voice_commands", "location_tracking"]
        })
        
        # Start location monitoring in background thread
        self.is_running = True
        location_thread = threading.Thread(target=self._location_monitor_loop, daemon=True)
        location_thread.start()
        
        print("✅ HINT Gateway Router started")
        print(f"🔄 Monitoring location updates every {self.update_interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        return True
    
    def _location_monitor_loop(self) -> None:
        """Background loop to monitor location updates"""
        while self.is_running:
            try:
                # Get latest location from Firebase
                location_data = self.firebase.get_latest_location()
                
                if location_data:
                    self._process_location_update(location_data)
                else:
                    print("📍 No location data available")
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"⚠️  Error in location monitor: {e}")
                time.sleep(self.update_interval)
    
    def _process_location_update(self, location_data: dict) -> None:
        """
        Process incoming location update
        
        Args:
            location_data: Location data from Firebase
        """
        try:
            location = location_data.get('location', {})
            lat = location.get('latitude')
            lng = location.get('longitude')
            timestamp = location_data.get('timestamp', time.time())
            
            if lat is None or lng is None:
                print("⚠️  Invalid location data received")
                return
            
            current_location = (lat, lng)
            self.last_location = current_location
            
            print(f"\n📍 Location Update: {lat:.4f}, {lng:.4f}")
            print(f"⏰ Timestamp: {time.ctime(timestamp)}")
            
            # If we have a destination, process navigation
            if self.current_destination and self.current_route:
                self._process_navigation(current_location)
            else:
                print("ℹ️  No active navigation - waiting for destination")
            
            # Send status update
            self.firebase.send_status_update("router", "location_received", {
                "location": current_location,
                "has_destination": self.current_destination is not None,
                "has_route": self.current_route is not None
            })
            
        except Exception as e:
            print(f"❌ Error processing location update: {e}")
    
    def _process_navigation(self, current_location: Tuple[float, float]) -> None:
        """
        Process navigation based on current location
        
        Args:
            current_location: Current (lat, lng) position
        """
        try:
            if not self.current_route:
                return
            
            steps = self.current_route.get('legs', [{}])[0].get('steps', [])
            if not steps:
                return
            
            # Find current step based on location
            current_step_idx = self.navigator.find_current_step(current_location, steps)
            
            if current_step_idx != self.current_step:
                self.current_step = current_step_idx
                step = steps[current_step_idx]
                
                # Format instruction for speech
                instruction = self._format_instruction_for_speech(step)
                
                print(f"\n🧭 Navigation Update (Step {current_step_idx + 1}/{len(steps)}):")
                print(f"   {instruction}")
                
                # Send voice command to laptop
                self.firebase.send_voice_command(instruction)
                
                # Check if we've arrived
                dest_coords = self._get_destination_coords()
                if dest_coords:
                    distance_to_dest = self.navigator.calculate_distance(current_location, dest_coords)
                    if distance_to_dest < 20:  # Within 20 meters
                        print("\n🎯 Arrived at destination!")
                        self.firebase.send_voice_command("You have arrived at your destination!")
                        self._stop_navigation()
            
        except Exception as e:
            print(f"❌ Error processing navigation: {e}")
    
    def _format_instruction_for_speech(self, step: dict) -> str:
        """
        Format navigation step for speech
        
        Args:
            step: Navigation step dictionary
            
        Returns:
            Speech-friendly instruction text
        """
        maneuver = step['maneuver']
        distance = step['distance']
        direction_type = maneuver['type']
        modifier = maneuver.get('modifier', '')
        instruction = step.get('name', 'the road')
        
        # Format distance
        if distance < 1000:
            dist_text = f"{int(distance)} meters"
        else:
            km = distance / 1000
            dist_text = f"{km:.1f} kilometers"
        
        # Create natural speech instruction
        if direction_type == 'depart':
            return f"Head {modifier} on {instruction} for {dist_text}"
        elif direction_type == 'arrive':
            return "You have arrived at your destination"
        elif direction_type == 'turn':
            return f"In {dist_text}, turn {modifier} onto {instruction}"
        elif direction_type == 'merge':
            return f"In {dist_text}, merge {modifier} onto {instruction}"
        elif direction_type == 'roundabout':
            exit_num = maneuver.get('exit', 1)
            return f"In {dist_text}, at the roundabout, take exit {exit_num} onto {instruction}"
        elif direction_type == 'fork':
            return f"In {dist_text}, at the fork, keep {modifier} onto {instruction}"
        else:
            return f"In {dist_text}, {direction_type.replace('_', ' ')} {modifier} onto {instruction}"
    
    def start_navigation(self, destination: str) -> bool:
        """
        Start navigation to destination
        
        Args:
            destination: Destination address
            
        Returns:
            bool: True if navigation started successfully
        """
        if not self.last_location:
            print("❌ No current location available")
            return False
        
        print(f"\n🧭 Starting navigation to: {destination}")
        
        # Get destination coordinates
        dest_coords = self.navigator.geocode(destination)
        if not dest_coords:
            print(f"❌ Could not find destination: {destination}")
            return False
        
        # Calculate route
        route_data = self.navigator.get_route(self.last_location, dest_coords)
        if not route_data or not route_data.get('routes'):
            print("❌ Could not find route to destination")
            return False
        
        # Store navigation data
        self.current_destination = destination
        self.current_route = route_data['routes'][0]
        self.current_step = 0
        
        # Send navigation start command
        self.firebase.send_navigation_command(destination, self.last_location)
        
        # Send initial instruction
        steps = self.current_route['legs'][0]['steps']
        if steps:
            instruction = self._format_instruction_for_speech(steps[0])
            self.firebase.send_voice_command(instruction)
        
        print("✅ Navigation started")
        return True
    
    def _get_destination_coords(self) -> Optional[Tuple[float, float]]:
        """Get destination coordinates if available"""
        if not self.current_destination:
            return None
        
        return self.navigator.geocode(self.current_destination)
    
    def _stop_navigation(self) -> None:
        """Stop current navigation"""
        self.current_destination = None
        self.current_route = None
        self.current_step = 0
        print("🛑 Navigation stopped")
    
    def stop_router(self) -> None:
        """Stop the Pi Router service"""
        print("\n🛑 Stopping HINT Gateway Router...")
        self.is_running = False
        
        # Send status update
        self.firebase.send_status_update("router", "stopped")
        
        # Close Firebase connection
        self.firebase.close()
        
        print("✅ HINT Gateway Router stopped")

def main():
    """Main function for Pi Router"""
    print("🌐 HINT Gateway - Raspberry Pi Router")
    print("=" * 50)
    
    # Create and start router
    router = PiRouter()
    
    if not router.start_router():
        print("❌ Failed to start router")
        sys.exit(1)
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        router.stop_router()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
