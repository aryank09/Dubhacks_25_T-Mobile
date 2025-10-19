#!/usr/bin/env python3
"""
GPS-Only Laptop Client for HINT System
Only sends GPS coordinates to Firebase - no voice interaction
"""

import time
import threading
import sys
from typing import Optional, Tuple
from firebase_client import FirebaseClient
from text_maps import TextMaps

class GPSLaptopClient:
    """GPS-Only Laptop Client that only sends location data"""
    
    def __init__(self):
        """Initialize the GPS Laptop Client"""
        self.firebase = FirebaseClient()
        self.navigator = TextMaps()
        self.is_running = False
        self.location_thread = None
        self.update_interval = 5  # Send location every 5 seconds
        self.current_location = None
        
        print("📍 GPS-Only HINT Laptop Client Initialized")
        print("=" * 50)
    
    def start_client(self) -> bool:
        """
        Start the GPS Laptop Client service
        
        Returns:
            bool: True if started successfully
        """
        if not self.firebase.is_ready():
            print("❌ Firebase not ready. Please check configuration.")
            return False
        
        print("🚀 Starting GPS-Only HINT Laptop Client...")
        
        # Send initial status
        self.firebase.send_status_update("client", "starting", {
            "update_interval": self.update_interval,
            "capabilities": ["location_tracking"],
            "mode": "gps_only"
        })
        
        # Start location tracking
        self.is_running = True
        self.location_thread = threading.Thread(target=self._location_tracking_loop, daemon=True)
        self.location_thread.start()
        
        print("✅ GPS-Only HINT Laptop Client started")
        print(f"📍 Sending GPS coordinates every {self.update_interval} seconds")
        print("📱 No voice interaction - Pi handles all navigation")
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
                            print(f"📍 GPS sent to Pi: {lat:.4f}, {lng:.4f}")
                            last_sent_location = current_location
                            location_failures = 0
                        else:
                            print("⚠️  Failed to send GPS coordinates")
                            location_failures += 1
                    else:
                        print(f"📍 GPS unchanged: {lat:.4f}, {lng:.4f}")
                else:
                    print("⚠️  Could not get GPS location")
                    location_failures += 1
                    
                    # If we've failed too many times, increase the interval
                    if location_failures > 5:
                        print("⚠️  Multiple GPS failures, increasing interval...")
                        time.sleep(30)  # Wait 30 seconds before trying again
                        continue
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"⚠️  Error in GPS tracking: {e}")
                time.sleep(self.update_interval)
    
    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current location
        
        Returns:
            Current (lat, lng) tuple or None
        """
        return self.current_location
    
    def stop_client(self) -> None:
        """Stop the GPS Laptop Client service"""
        print("\n🛑 Stopping GPS-Only HINT Laptop Client...")
        self.is_running = False
        
        # Wait for location thread to finish
        if self.location_thread and self.location_thread.is_alive():
            self.location_thread.join(timeout=2)
        
        # Send status update
        self.firebase.send_status_update("client", "stopped")
        
        # Close Firebase connection
        self.firebase.close()
        
        print("✅ GPS-Only HINT Laptop Client stopped")

def main():
    """Main function for GPS Laptop Client"""
    print("📍 GPS-Only HINT Laptop Client")
    print("=" * 50)
    
    # Create and start client
    client = GPSLaptopClient()
    
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
