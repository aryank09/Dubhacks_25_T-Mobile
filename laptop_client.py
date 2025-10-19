#!/usr/bin/env python3
"""
Laptop Client for HINT System
Sends location data to Firebase and listens for commands from the Pi Router
"""

import time
import threading
import sys
from typing import Optional, Tuple
from firebase_client import FirebaseClient
from firebase_config import MessageTypes
from text_maps import TextMaps
from TTS import say

class LaptopClient:
    """Laptop Client for HINT system"""
    
    def __init__(self):
        """Initialize the Laptop Client"""
        self.firebase = FirebaseClient()
        self.navigator = TextMaps()
        self.is_running = False
        self.location_thread = None
        self.command_thread = None
        self.update_interval = 5  # Send location every 5 seconds
        self.current_location = None
        
        print("💻 HINT Laptop Client Initialized")
        print("=" * 50)
    
    def start_client(self) -> bool:
        """
        Start the Laptop Client service
        
        Returns:
            bool: True if started successfully
        """
        if not self.firebase.is_ready():
            print("❌ Firebase not ready. Please check configuration.")
            return False
        
        print("🚀 Starting HINT Laptop Client...")
        
        # Send initial status
        self.firebase.send_status_update("client", "starting", {
            "update_interval": self.update_interval,
            "capabilities": ["location_tracking", "voice_output", "command_processing"]
        })
        
        # Start location tracking
        self.is_running = True
        self.location_thread = threading.Thread(target=self._location_tracking_loop, daemon=True)
        self.location_thread.start()
        
        # Start command listening
        self.command_thread = threading.Thread(target=self._command_listening_loop, daemon=True)
        self.command_thread.start()
        
        print("✅ HINT Laptop Client started")
        print(f"📍 Sending location updates every {self.update_interval} seconds")
        print("👂 Listening for commands from Pi Router")
        print("Press Ctrl+C to stop\n")
        
        return True
    
    def _location_tracking_loop(self) -> None:
        """Background loop to track and send location updates"""
        while self.is_running:
            try:
                # Get current location
                current_location = self.navigator.get_current_location()
                
                if current_location:
                    lat, lng = current_location
                    self.current_location = current_location
                    
                    # Send location to Firebase
                    success = self.firebase.send_location_update(lat, lng)
                    
                    if success:
                        print(f"📍 Location sent: {lat:.4f}, {lng:.4f}")
                    else:
                        print("⚠️  Failed to send location")
                else:
                    print("⚠️  Could not get current location")
                
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
                    self._process_command(command_data)
                
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
    
    def stop_client(self) -> None:
        """Stop the Laptop Client service"""
        print("\n🛑 Stopping HINT Laptop Client...")
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
        
        print("✅ HINT Laptop Client stopped")

def main():
    """Main function for Laptop Client"""
    print("💻 HINT Laptop Client")
    print("=" * 50)
    
    # Create and start client
    client = LaptopClient()
    
    if not client.start_client():
        print("❌ Failed to start client")
        sys.exit(1)
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        client.stop_client()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
