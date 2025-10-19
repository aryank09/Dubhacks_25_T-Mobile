#!/usr/bin/env python3
"""
Enhanced Laptop Client for HINT System
Integrates voice prompting features from main.py with Firebase communication
"""

import time
import threading
import sys
from typing import Optional, Tuple
from firebase_client import FirebaseClient
from firebase_config import MessageTypes
from text_maps import TextMaps
from TTS import say, get_yes_no_confirmation, listen_for_input

class EnhancedLaptopClient:
    """Enhanced Laptop Client with voice prompting capabilities"""
    
    def __init__(self):
        """Initialize the Enhanced Laptop Client"""
        self.firebase = FirebaseClient()
        self.navigator = TextMaps()
        self.is_running = False
        self.location_thread = None
        self.command_thread = None
        self.update_interval = 5  # Send location every 5 seconds
        self.current_location = None
        self.last_processed_command = None  # Track last command to avoid duplicates
        
        print("💻 Enhanced HINT Laptop Client Initialized")
        print("=" * 50)
    
    def start_client(self) -> bool:
        """
        Start the Enhanced Laptop Client service
        
        Returns:
            bool: True if started successfully
        """
        if not self.firebase.is_ready():
            print("❌ Firebase not ready. Please check configuration.")
            return False
        
        print("🚀 Starting Enhanced HINT Laptop Client...")
        
        # Send initial status
        self.firebase.send_status_update("client", "starting", {
            "update_interval": self.update_interval,
            "capabilities": ["location_tracking", "voice_output", "command_processing", "voice_input"]
        })
        
        # Start location tracking
        self.is_running = True
        self.location_thread = threading.Thread(target=self._location_tracking_loop, daemon=True)
        self.location_thread.start()
        
        # Start command listening
        self.command_thread = threading.Thread(target=self._command_listening_loop, daemon=True)
        self.command_thread.start()
        
        print("✅ Enhanced HINT Laptop Client started")
        print(f"📍 Sending location updates every {self.update_interval} seconds")
        print("👂 Listening for commands from Pi Router")
        print("🎤 Voice input capabilities enabled")
        print("Press Ctrl+C to stop\n")
        
        return True
    
    def _location_tracking_loop(self) -> None:
        """Background loop to track and send location updates"""
        last_sent_location = None
        location_failures = 0
        
        while self.is_running:
            try:
                # Get current location
                current_location = self.navigator.get_current_location()
                
                if current_location:
                    lat, lng = current_location
                    self.current_location = current_location
                    
                    # Only send if location changed significantly (more than 10 meters)
                    should_send = True
                    if last_sent_location:
                        distance = self.navigator.calculate_distance(last_sent_location, current_location)
                        should_send = distance > 10  # Only send if moved more than 10 meters
                    
                    if should_send:
                        # Send location to Firebase
                        success = self.firebase.send_location_update(lat, lng)
                        
                        if success:
                            print(f"📍 Location sent: {lat:.4f}, {lng:.4f}")
                            last_sent_location = current_location
                            location_failures = 0
                        else:
                            print("⚠️  Failed to send location")
                            location_failures += 1
                    else:
                        print(f"📍 Location unchanged: {lat:.4f}, {lng:.4f}")
                else:
                    print("⚠️  Could not get current location")
                    location_failures += 1
                    
                    # If we've failed too many times, increase the interval
                    if location_failures > 5:
                        print("⚠️  Multiple location failures, increasing interval...")
                        time.sleep(30)  # Wait 30 seconds before trying again
                        continue
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"⚠️  Error in location tracking: {e}")
                time.sleep(self.update_interval)
    
    def _command_listening_loop(self) -> None:
        """Background loop to listen for commands from Pi Router"""
        while self.is_running:
            try:
                # Get latest command from Firebase
                command_data = self.firebase.get_latest_command()
                
                if command_data:
                    # Check if this is a new command (avoid processing duplicates)
                    command_id = f"{command_data.get('type', '')}_{command_data.get('timestamp', 0)}"
                    if command_id != self.last_processed_command:
                        self._process_command(command_data)
                        self.last_processed_command = command_id
                
                # Check for commands every second
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️  Error in command listening: {e}")
                time.sleep(1)
    
    def _process_command(self, command_data: dict) -> None:
        """
        Process incoming command from Pi Router
        
        Args:
            command_data: Command data from Firebase
        """
        try:
            command_type = command_data.get('type')
            data = command_data.get('data', {})
            timestamp = command_data.get('timestamp', time.time())
            
            print(f"\n📨 Command received: {command_type}")
            print(f"⏰ Timestamp: {time.ctime(timestamp)}")
            
            if command_type == MessageTypes.NAVIGATION_START:
                self._handle_navigation_start(data)
            elif command_type == MessageTypes.NAVIGATION_STOP:
                self._handle_navigation_stop(data)
            elif command_type == MessageTypes.VOICE_COMMAND:
                self._handle_voice_command(data)
            elif command_type == MessageTypes.SYSTEM_COMMAND:
                self._handle_system_command(data)
            else:
                print(f"⚠️  Unknown command type: {command_type}")
            
        except Exception as e:
            print(f"❌ Error processing command: {e}")
    
    def _handle_navigation_start(self, data: dict) -> None:
        """
        Handle navigation start command
        
        Args:
            data: Navigation command data
        """
        destination = data.get('destination', 'Unknown destination')
        current_location = data.get('current_location', {})
        
        print(f"\n🧭 Navigation Started")
        print(f"📍 Destination: {destination}")
        print(f"📍 Current: {current_location.get('latitude', 'N/A'):.4f}, {current_location.get('longitude', 'N/A'):.4f}")
        
        # Speak navigation start message
        message = f"Navigation started to {destination}"
        say(message)
    
    def _handle_navigation_stop(self, data: dict) -> None:
        """
        Handle navigation stop command
        
        Args:
            data: Navigation stop data
        """
        print(f"\n🛑 Navigation Stopped")
        
        # Speak navigation stop message
        say("Navigation stopped")
    
    def _handle_voice_command(self, data: dict) -> None:
        """
        Handle voice command from Pi Router
        
        Args:
            data: Voice command data
        """
        text = data.get('text', '')
        
        if text:
            # Skip test commands to avoid spam
            if "test" in text.lower() and "firebase" in text.lower():
                print(f"\n🎤 Test Voice Command (skipped): {text}")
                return
                
            print(f"\n🎤 Voice Command: {text}")
            
            # Speak the command
            say(text)
        else:
            print("⚠️  Empty voice command received")
    
    def _handle_system_command(self, data: dict) -> None:
        """
        Handle system command from Pi Router
        
        Args:
            data: System command data
        """
        command = data.get('command', '')
        message = data.get('message', '')
        
        print(f"\n⚙️  System Command: {command}")
        if message:
            print(f"📝 Message: {message}")
            
            # Speak system message if provided
            if message:
                say(message)
    
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
    
    def send_manual_location(self, latitude: float, longitude: float) -> bool:
        """
        Manually send location update (for testing)
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            
        Returns:
            bool: True if successful
        """
        return self.firebase.send_location_update(latitude, longitude)
    
    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current location
        
        Returns:
            Current (lat, lng) tuple or None
        """
        return self.current_location
    
    def interactive_mode(self):
        """
        Interactive mode for voice input and testing
        """
        print("\n🎤 Interactive Mode - Voice Commands")
        print("=" * 50)
        print("Available commands:")
        print("1. Get destination by voice")
        print("2. Send test location")
        print("3. Send test voice command")
        print("4. Exit interactive mode")
        
        while True:
            try:
                choice = input("\nEnter choice (1-4): ").strip()
                
                if choice == "1":
                    destination = self.get_destination_by_voice()
                    if destination:
                        if self.confirm_destination(destination):
                            print(f"✅ Destination confirmed: {destination}")
                            # Send navigation request to Pi
                            self.firebase.send_navigation_command(destination, self.current_location or (0, 0))
                        else:
                            print("❌ Destination not confirmed")
                    else:
                        print("❌ Could not get destination")
                
                elif choice == "2":
                    if self.current_location:
                        success = self.send_manual_location(*self.current_location)
                        print(f"📍 Test location sent: {'Success' if success else 'Failed'}")
                    else:
                        print("❌ No current location available")
                
                elif choice == "3":
                    text = input("Enter text to send as voice command: ").strip()
                    if text:
                        success = self.firebase.send_voice_command(text)
                        print(f"🎤 Test voice command sent: {'Success' if success else 'Failed'}")
                
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
    
    def stop_client(self) -> None:
        """Stop the Enhanced Laptop Client service"""
        print("\n🛑 Stopping Enhanced HINT Laptop Client...")
        self.is_running = False
        
        # Wait for threads to finish
        if self.location_thread and self.location_thread.is_alive():
            self.location_thread.join(timeout=2)
        
        if self.command_thread and self.command_thread.is_alive():
            self.command_thread.join(timeout=2)
        
        # Send status update
        self.firebase.send_status_update("client", "stopped")
        
        # Close Firebase connection
        self.firebase.close()
        
        print("✅ Enhanced HINT Laptop Client stopped")

def main():
    """Main function for Enhanced Laptop Client"""
    print("💻 Enhanced HINT Laptop Client")
    print("=" * 50)
    
    # Create and start client
    client = EnhancedLaptopClient()
    
    if not client.start_client():
        print("❌ Failed to start client")
        sys.exit(1)
    
    try:
        # Check if user wants interactive mode
        print("\nWould you like to enter interactive mode? (y/N): ", end="")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                client.interactive_mode()
        except (KeyboardInterrupt, EOFError):
            print("\nContinuing in background mode...")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        client.stop_client()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
