#!/usr/bin/env python3
"""
Raspberry Pi Navigation Router for HINT System
Runs the full navigation program with voice interaction, pulling GPS from Firebase
"""

import time
import threading
import sys
from typing import Optional, Tuple
from firebase_client import FirebaseClient
from firebase_config import MessageTypes
from text_maps import TextMaps
from TTS import say, get_yes_no_confirmation, listen_for_input

class PiNavigationRouter:
    """Raspberry Pi Router that runs full navigation with voice interaction"""
    
    def __init__(self):
        """Initialize the Pi Navigation Router"""
        self.firebase = FirebaseClient()
        self.navigator = TextMaps()
        self.is_running = False
        self.location_thread = None
        self.current_destination = None
        self.current_route = None
        self.current_step = 0
        self.last_location = None
        self.update_interval = 5  # Pull location every 5 seconds
        self.last_spoken_step = -1
        
        print("🌐 HINT Pi Navigation Router Initialized")
        print("=" * 60)
    
    def start_router(self) -> bool:
        """
        Start the Pi Navigation Router service
        
        Returns:
            bool: True if started successfully
        """
        if not self.firebase.is_ready():
            print("❌ Firebase not ready. Please check configuration.")
            return False
        
        print("🚀 Starting HINT Pi Navigation Router...")
        
        # Send initial status
        self.firebase.send_status_update("router", "starting", {
            "update_interval": self.update_interval,
            "capabilities": ["navigation", "voice_commands", "location_tracking", "voice_input"]
        })
        
        # Start location monitoring in background thread
        self.is_running = True
        self.location_thread = threading.Thread(target=self._location_monitor_loop, daemon=True)
        self.location_thread.start()
        
        print("✅ HINT Pi Navigation Router started")
        print(f"🔄 Monitoring location updates every {self.update_interval} seconds")
        print("🎤 Voice interaction enabled")
        print("Press Ctrl+C to stop\n")
        
        return True
    
    def _location_monitor_loop(self) -> None:
        """Background loop to monitor location updates from laptop"""
        while self.is_running:
            try:
                # Get latest location from Firebase
                location_data = self.firebase.get_latest_location()
                
                if location_data:
                    self._process_location_update(location_data)
                else:
                    print("📍 No location data available from laptop")
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"⚠️  Error in location monitor: {e}")
                time.sleep(self.update_interval)
    
    def _process_location_update(self, location_data: dict) -> None:
        """
        Process incoming location update from laptop
        
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
            
            print(f"\n📍 Location Update from Laptop: {lat:.4f}, {lng:.4f}")
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
                
                # Speak instruction
                say(instruction)
                
                # Check if we've arrived
                dest_coords = self._get_destination_coords()
                if dest_coords:
                    distance_to_dest = self.navigator.calculate_distance(current_location, dest_coords)
                    if distance_to_dest < 20:  # Within 20 meters
                        print("\n🎯 Arrived at destination!")
                        say("You have arrived at your destination!")
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
    
    def get_destination_by_voice(self) -> str:
        """
        Get destination from voice input (from main.py)
        
        Returns:
            str: The destination address, or None if no valid input
        """
        print(f"\n{'='*60}")
        print(f"🎤 VOICE DESTINATION INPUT")
        print(f"{'='*60}")
        print("Please speak your destination address clearly.")
        print(f"{'='*60}\n")
        
        # Ask for destination
        say("Please tell me your destination address.")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            print(f"\n🔄 Voice input attempt {attempt + 1}/{max_attempts}")
            
            destination = listen_for_input(timeout=15, phrase_time_limit=10)
            
            if destination and len(destination.strip()) > 0:
                print(f"🎤 Heard destination: {destination}")
                return destination.strip()
            else:
                print("⚠️  No destination heard or destination too short")
                if attempt < max_attempts - 1:
                    say("I didn't hear a destination. Please try again.")
                else:
                    say("I'm having trouble hearing your destination. Please try again later.")
                    return None
        
        return None
    
    def confirm_destination(self, destination: str) -> bool:
        """
        Confirm destination with voice input (from main.py)
        
        Args:
            destination: The destination address to confirm
            
        Returns:
            bool: True if confirmed, False if not confirmed or error
        """
        print(f"\n{'='*60}")
        print(f"🎤 VOICE DESTINATION CONFIRMATION")
        print(f"{'='*60}")
        print(f"📍 Destination: {destination}")
        print(f"{'='*60}\n")
        
        # Ask for confirmation with voice
        confirmation_question = f"I heard your destination as {destination}. Is this correct? Please say yes or no."
        
        max_attempts = 3
        for attempt in range(max_attempts):
            print(f"\n🔄 Confirmation attempt {attempt + 1}/{max_attempts}")
            
            response = get_yes_no_confirmation(confirmation_question, timeout=15)
            
            if response is True:
                print("✅ Destination confirmed!")
                say("Great! Starting navigation to " + destination)
                return True
            elif response is False:
                print("❌ Destination not confirmed")
                say("I understand. Please try again with a different destination.")
                return False
            else:
                print("⚠️  Could not understand your response")
                if attempt < max_attempts - 1:
                    say("I didn't catch that. Please say yes or no.")
                else:
                    say("I'm having trouble understanding. Please try again later.")
                    return False
        
        return False
    
    def start_navigation(self, destination: str) -> bool:
        """
        Start navigation to destination
        
        Args:
            destination: Destination address
            
        Returns:
            bool: True if navigation started successfully
        """
        if not self.last_location:
            print("❌ No current location available from laptop")
            say("I don't have your current location from the laptop. Please make sure the laptop is running.")
            return False
        
        print(f"\n🧭 Starting navigation to: {destination}")
        
        # Get destination coordinates
        dest_coords = self.navigator.geocode(destination)
        if not dest_coords:
            print(f"❌ Could not find destination: {destination}")
            say(f"Error: Could not find destination {destination}")
            return False
        
        # Calculate route
        route_data = self.navigator.get_route(self.last_location, dest_coords)
        if not route_data or not route_data.get('routes'):
            print("❌ Could not find route to destination")
            say("Error: Could not find a route to your destination")
            return False
        
        # Store navigation data
        self.current_destination = destination
        self.current_route = route_data['routes'][0]
        self.current_step = 0
        
        # Announce route summary
        route = self.current_route
        steps = route['legs'][0]['steps']
        total_distance = route['distance']
        total_duration = route['duration']
        
        print(f"{'='*60}")
        print(f"📊 ROUTE OVERVIEW")
        print(f"{'='*60}")
        print(f"Total Distance: {self.navigator.format_distance(total_distance)}")
        print(f"Estimated Time: {self.navigator.format_duration(total_duration)}")
        print(f"Total Steps: {len(steps)}")
        print(f"{'='*60}\n")
        
        summary = f"Route calculated. Total distance is {self.navigator.format_distance(total_distance)}. Estimated time is {self.navigator.format_duration(total_duration)}. Starting navigation."
        say(summary)
        
        # Send initial instruction
        if steps:
            instruction = self._format_instruction_for_speech(steps[0])
            say(instruction)
        
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
    
    def interactive_mode(self):
        """
        Interactive mode for voice input and navigation control
        """
        print("\n🎤 Interactive Navigation Mode")
        print("=" * 50)
        print("Available commands:")
        print("1. Start navigation by voice")
        print("2. Stop current navigation")
        print("3. Check current location")
        print("4. Exit interactive mode")
        
        while True:
            try:
                choice = input("\nEnter choice (1-4): ").strip()
                
                if choice == "1":
                    destination = self.get_destination_by_voice()
                    if destination:
                        if self.confirm_destination(destination):
                            print(f"✅ Destination confirmed: {destination}")
                            self.start_navigation(destination)
                        else:
                            print("❌ Destination not confirmed")
                    else:
                        print("❌ Could not get destination")
                
                elif choice == "2":
                    if self.current_destination:
                        self._stop_navigation()
                        say("Navigation stopped")
                        print("✅ Navigation stopped")
                    else:
                        print("❌ No active navigation")
                
                elif choice == "3":
                    if self.last_location:
                        lat, lng = self.last_location
                        print(f"📍 Current location: {lat:.4f}, {lng:.4f}")
                        say(f"Current location is {lat:.4f}, {lng:.4f}")
                    else:
                        print("❌ No location data available")
                        say("No location data available from laptop")
                
                elif choice == "4":
                    print("👋 Exiting interactive mode")
                    break
                
                else:
                    print("❌ Invalid choice. Please enter 1-4.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting interactive mode")
                break
            except Exception as e:
                print(f"❌ Error in interactive mode: {e}")
    
    def stop_router(self) -> None:
        """Stop the Pi Navigation Router service"""
        print("\n🛑 Stopping HINT Pi Navigation Router...")
        self.is_running = False
        
        # Wait for location thread to finish
        if self.location_thread and self.location_thread.is_alive():
            self.location_thread.join(timeout=2)
        
        # Send status update
        self.firebase.send_status_update("router", "stopped")
        
        # Close Firebase connection
        self.firebase.close()
        
        print("✅ HINT Pi Navigation Router stopped")

def main():
    """Main function for Pi Navigation Router"""
    print("🌐 HINT Pi Navigation Router")
    print("=" * 60)
    
    # Create and start router
    router = PiNavigationRouter()
    
    if not router.start_router():
        print("❌ Failed to start router")
        sys.exit(1)
    
    try:
        # Check if user wants interactive mode
        print("\nWould you like to enter interactive navigation mode? (y/N): ", end="")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                router.interactive_mode()
        except (KeyboardInterrupt, EOFError):
            print("\nContinuing in background mode...")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        router.stop_router()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
