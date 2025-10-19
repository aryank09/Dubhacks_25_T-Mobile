#!/usr/bin/env python3
"""
Firebase Client for HINT Gateway System
Handles Firebase Realtime Database communication for both Pi (Router) and Laptop (Client)
"""

import time
import json
import threading
import requests
from typing import Callable, Dict, Any, Optional, List
from firebase_config import FirebaseConfig, DatabasePaths, MessageTypes, MessageTemplates

class FirebaseClient:
    """Firebase Realtime Database client for HINT Gateway system"""
    
    def __init__(self, config_file: str = "firebase_config.json"):
        """
        Initialize Firebase client
        
        Args:
            config_file: Path to Firebase configuration file
        """
        self.config_manager = FirebaseConfig(config_file)
        self.config = self.config_manager.get_config()
        self.db = None
        self.listeners = {}  # Store active listeners
        self.is_connected = False
        
        # Initialize Firebase connection
        self._initialize_firebase()
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase connection"""
        try:
            if not self.config_manager.is_configured():
                print("❌ Firebase not properly configured. Please update firebase_config.json")
                return
            
            # Initialize Firebase REST API connection
            self.database_url = self.config_manager.get_database_url()
            if not self.database_url.endswith('/'):
                self.database_url += '/'
            
            self.is_connected = True
            print("✅ Firebase connected successfully")
            
        except Exception as e:
            print(f"❌ Firebase connection failed: {e}")
            self.is_connected = False
    
    def is_ready(self) -> bool:
        """Check if Firebase client is ready"""
        return self.is_connected and hasattr(self, 'database_url')
    
    def send_location_update(self, latitude: float, longitude: float, accuracy: float = 0.0) -> bool:
        """
        Send location update to Firebase (used by laptop client)
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            accuracy: GPS accuracy in meters
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_ready():
            print("❌ Firebase not ready")
            return False
        
        try:
            timestamp = time.time()
            message = MessageTemplates.location_message(latitude, longitude, timestamp, accuracy)
            
            # Send to Firebase using REST API
            url = f"{self.database_url}{DatabasePaths.USER_LOCATION}.json"
            response = requests.put(url, json=message, timeout=10)
            response.raise_for_status()
            
            print(f"📍 Location sent: {latitude:.4f}, {longitude:.4f}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending location: {e}")
            return False
    
    def send_command(self, command_type: str, data: Dict[str, Any]) -> bool:
        """
        Send command to Firebase (used by Pi router)
        
        Args:
            command_type: Type of command (from MessageTypes)
            data: Command data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_ready():
            print("❌ Firebase not ready")
            return False
        
        try:
            timestamp = time.time()
            message = MessageTemplates.command_message(command_type, data, timestamp)
            
            # Send to Firebase using REST API
            url = f"{self.database_url}{DatabasePaths.USER_COMMAND}.json"
            response = requests.put(url, json=message, timeout=10)
            response.raise_for_status()
            
            print(f"📤 Command sent: {command_type}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return False
    
    def send_navigation_command(self, destination: str, current_location: tuple) -> bool:
        """
        Send navigation start command (used by Pi router)
        
        Args:
            destination: Destination address
            current_location: Current (lat, lng) tuple
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_ready():
            return False
        
        try:
            timestamp = time.time()
            message = MessageTemplates.navigation_command(destination, current_location, timestamp)
            
            # Send to Firebase using REST API
            url = f"{self.database_url}{DatabasePaths.USER_COMMAND}.json"
            response = requests.put(url, json=message, timeout=10)
            response.raise_for_status()
            
            print(f"🧭 Navigation command sent: {destination}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending navigation command: {e}")
            return False
    
    def send_voice_command(self, text: str) -> bool:
        """
        Send voice command (used by Pi router)
        
        Args:
            text: Voice command text
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_ready():
            return False
        
        try:
            timestamp = time.time()
            message = MessageTemplates.voice_command(text, timestamp)
            
            # Send to Firebase using REST API
            url = f"{self.database_url}{DatabasePaths.USER_COMMAND}.json"
            response = requests.put(url, json=message, timeout=10)
            response.raise_for_status()
            
            print(f"🎤 Voice command sent: {text}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending voice command: {e}")
            return False
    
    def listen_for_location_updates(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Listen for location updates from laptop (used by Pi router)
        Note: This is a simplified implementation that polls instead of streaming
        
        Args:
            callback: Function to call when location update received
            
        Returns:
            bool: True if listener started successfully
        """
        if not self.is_ready():
            print("❌ Firebase not ready")
            return False
        
        try:
            def poll_location():
                last_data = None
                while self.listeners.get('location', False):
                    try:
                        url = f"{self.database_url}{DatabasePaths.USER_LOCATION}.json"
                        response = requests.get(url, timeout=5)
                        response.raise_for_status()
                        data = response.json()
                        
                        if data and data != last_data:
                            callback(data)
                            last_data = data
                        
                        time.sleep(1)  # Poll every second
                    except Exception as e:
                        print(f"⚠️  Error polling location: {e}")
                        time.sleep(5)
            
            self.listeners['location'] = True
            thread = threading.Thread(target=poll_location, daemon=True)
            thread.start()
            print("👂 Listening for location updates...")
            return True
            
        except Exception as e:
            print(f"❌ Error starting location listener: {e}")
            return False
    
    def listen_for_commands(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Listen for commands from Pi router (used by laptop client)
        Note: This is a simplified implementation that polls instead of streaming
        
        Args:
            callback: Function to call when command received
            
        Returns:
            bool: True if listener started successfully
        """
        if not self.is_ready():
            print("❌ Firebase not ready")
            return False
        
        try:
            def poll_commands():
                last_data = None
                while self.listeners.get('commands', False):
                    try:
                        url = f"{self.database_url}{DatabasePaths.USER_COMMAND}.json"
                        response = requests.get(url, timeout=5)
                        response.raise_for_status()
                        data = response.json()
                        
                        if data and data != last_data:
                            callback(data)
                            last_data = data
                        
                        time.sleep(1)  # Poll every second
                    except Exception as e:
                        print(f"⚠️  Error polling commands: {e}")
                        time.sleep(5)
            
            self.listeners['commands'] = True
            thread = threading.Thread(target=poll_commands, daemon=True)
            thread.start()
            print("👂 Listening for commands...")
            return True
            
        except Exception as e:
            print(f"❌ Error starting command listener: {e}")
            return False
    
    def get_latest_location(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest location data (used by Pi router)
        
        Returns:
            Dict with location data or None if not available
        """
        if not self.is_ready():
            return None
        
        try:
            url = f"{self.database_url}{DatabasePaths.USER_LOCATION}.json"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data if data else None
            
        except Exception as e:
            print(f"❌ Error getting latest location: {e}")
            return None
    
    def get_latest_command(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest command data (used by laptop client)
        
        Returns:
            Dict with command data or None if not available
        """
        if not self.is_ready():
            return None
        
        try:
            url = f"{self.database_url}{DatabasePaths.USER_COMMAND}.json"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data if data else None
            
        except Exception as e:
            print(f"❌ Error getting latest command: {e}")
            return None
    
    def send_status_update(self, device_type: str, status: str, details: Dict[str, Any] = None) -> bool:
        """
        Send status update to Firebase
        
        Args:
            device_type: "router" or "client"
            status: Status message
            details: Additional status details
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_ready():
            return False
        
        try:
            timestamp = time.time()
            message = MessageTemplates.status_message(status, device_type, timestamp, details)
            
            # Send to appropriate status path using REST API
            if device_type == "router":
                url = f"{self.database_url}{DatabasePaths.ROUTER_STATUS}.json"
            else:
                url = f"{self.database_url}{DatabasePaths.CLIENT_STATUS}.json"
            
            response = requests.put(url, json=message, timeout=10)
            response.raise_for_status()
            
            print(f"📊 Status update sent: {device_type} - {status}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending status update: {e}")
            return False
    
    def stop_listeners(self) -> None:
        """Stop all active listeners"""
        for listener_name in list(self.listeners.keys()):
            try:
                # Note: pyrebase4 doesn't have explicit stop method
                # Listeners will stop when the connection is closed
                del self.listeners[listener_name]
                print(f"🛑 Stopped {listener_name} listener")
            except Exception as e:
                print(f"⚠️  Error stopping {listener_name} listener: {e}")
    
    def close(self) -> None:
        """Close Firebase connection"""
        self.stop_listeners()
        self.is_connected = False
        print("🔌 Firebase connection closed")
