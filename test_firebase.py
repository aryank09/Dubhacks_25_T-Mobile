#!/usr/bin/env python3
"""
Test Firebase connection and basic functionality
"""

from firebase_client import FirebaseClient
import time

def test_firebase_connection():
    """Test Firebase connection and basic operations"""
    print("🧪 Testing Firebase Connection")
    print("=" * 40)
    
    # Initialize Firebase client
    client = FirebaseClient()
    
    if not client.is_ready():
        print("❌ Firebase not ready. Please check your configuration.")
        return False
    
    print("✅ Firebase client initialized successfully")
    
    # Test sending a location update
    print("\n📍 Testing location update...")
    success = client.send_location_update(47.6062, -122.3321, 5.0)
    if success:
        print("✅ Location update sent successfully")
    else:
        print("❌ Failed to send location update")
        return False
    
    # Test sending a voice command
    print("\n🎤 Testing voice command...")
    success = client.send_voice_command("Test voice command from Firebase")
    if success:
        print("✅ Voice command sent successfully")
    else:
        print("❌ Failed to send voice command")
        return False
    
    # Test sending status update
    print("\n📊 Testing status update...")
    success = client.send_status_update("test", "connection_test", {
        "message": "Firebase test successful",
        "timestamp": time.time()
    })
    if success:
        print("✅ Status update sent successfully")
    else:
        print("❌ Failed to send status update")
        return False
    
    # Test getting latest data
    print("\n📥 Testing data retrieval...")
    location_data = client.get_latest_location()
    if location_data:
        print(f"✅ Latest location retrieved: {location_data}")
    else:
        print("⚠️  No location data found")
    
    command_data = client.get_latest_command()
    if command_data:
        print(f"✅ Latest command retrieved: {command_data}")
    else:
        print("⚠️  No command data found")
    
    print("\n🎉 Firebase test completed successfully!")
    return True

if __name__ == "__main__":
    test_firebase_connection()
