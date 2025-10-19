#!/usr/bin/env python3
"""
Firebase Configuration for HINT Gateway System
Raspberry Pi (Router) and Laptop (Client) communication via Firebase Realtime Database
"""

import os
import json
from typing import Dict, Any, Optional

class FirebaseConfig:
    """Firebase configuration and connection management"""
    
    def __init__(self, config_file: str = "firebase_config.json"):
        """
        Initialize Firebase configuration
        
        Args:
            config_file: Path to Firebase configuration JSON file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Firebase configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading Firebase config: {e}")
                return self._get_default_config()
        else:
            print(f"⚠️  Firebase config file not found: {self.config_file}")
            print("📝 Creating default config file...")
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default Firebase configuration"""
        return {
            "apiKey": "your-api-key-here",
            "authDomain": "your-project-id.firebaseapp.com",
            "databaseURL": "https://your-project-id-default-rtdb.firebaseio.com/",
            "projectId": "your-project-id",
            "storageBucket": "your-project-id.appspot.com",
            "messagingSenderId": "123456789",
            "appId": "your-app-id"
        }
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Firebase config saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving Firebase config: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current Firebase configuration"""
        return self.config
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update Firebase configuration"""
        self.config.update(new_config)
        self._save_config(self.config)
    
    def is_configured(self) -> bool:
        """Check if Firebase is properly configured"""
        required_keys = ["apiKey", "authDomain", "databaseURL", "projectId"]
        return all(
            key in self.config and 
            self.config[key] != f"your-{key.replace('Id', '-id').replace('Key', '-key')}-here"
            for key in required_keys
        )
    
    def get_database_url(self) -> str:
        """Get Firebase Realtime Database URL"""
        return self.config.get("databaseURL", "")
    
    def get_api_key(self) -> str:
        """Get Firebase API key"""
        return self.config.get("apiKey", "")

# Database paths for the HINT Gateway system
class DatabasePaths:
    """Firebase Realtime Database paths for HINT Gateway system"""
    
    # Location data from laptop (client) to Pi (router)
    USER_LOCATION = "/user/location"
    
    # Commands from Pi (router) to laptop (client)
    USER_COMMAND = "/user/command"
    
    # System status and metadata
    SYSTEM_STATUS = "/system/status"
    ROUTER_STATUS = "/system/router"
    CLIENT_STATUS = "/system/client"

# Message types for communication
class MessageTypes:
    """Message types for Pi-Laptop communication"""
    
    # Location messages from laptop
    LOCATION_UPDATE = "location_update"
    LOCATION_REQUEST = "location_request"
    
    # Command messages from Pi
    NAVIGATION_START = "navigation_start"
    NAVIGATION_STOP = "navigation_stop"
    NAVIGATION_UPDATE = "navigation_update"
    VOICE_COMMAND = "voice_command"
    SYSTEM_COMMAND = "system_command"
    
    # Status messages
    STATUS_UPDATE = "status_update"
    CONNECTION_ALIVE = "connection_alive"
    ERROR_MESSAGE = "error_message"

# Message structure templates
class MessageTemplates:
    """Templates for structured messages"""
    
    @staticmethod
    def location_message(lat: float, lng: float, timestamp: float, accuracy: float = 0.0) -> Dict[str, Any]:
        """Create a location update message"""
        return {
            "type": MessageTypes.LOCATION_UPDATE,
            "timestamp": timestamp,
            "location": {
                "latitude": lat,
                "longitude": lng,
                "accuracy": accuracy
            }
        }
    
    @staticmethod
    def command_message(command_type: str, data: Dict[str, Any], timestamp: float) -> Dict[str, Any]:
        """Create a command message"""
        return {
            "type": command_type,
            "timestamp": timestamp,
            "data": data
        }
    
    @staticmethod
    def navigation_command(destination: str, current_location: tuple, timestamp: float) -> Dict[str, Any]:
        """Create a navigation start command"""
        return {
            "type": MessageTypes.NAVIGATION_START,
            "timestamp": timestamp,
            "data": {
                "destination": destination,
                "current_location": {
                    "latitude": current_location[0],
                    "longitude": current_location[1]
                }
            }
        }
    
    @staticmethod
    def voice_command(text: str, timestamp: float) -> Dict[str, Any]:
        """Create a voice command message"""
        return {
            "type": MessageTypes.VOICE_COMMAND,
            "timestamp": timestamp,
            "data": {
                "text": text
            }
        }
    
    @staticmethod
    def status_message(status: str, device_type: str, timestamp: float, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a status update message"""
        return {
            "type": MessageTypes.STATUS_UPDATE,
            "timestamp": timestamp,
            "data": {
                "status": status,
                "device_type": device_type,
                "details": details or {}
            }
        }
