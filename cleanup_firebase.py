#!/usr/bin/env python3
"""
Clean up Firebase test data
"""

from firebase_client import FirebaseClient
import requests

def cleanup_firebase():
    """Clean up test data from Firebase"""
    print("🧹 Cleaning up Firebase test data...")
    
    client = FirebaseClient()
    
    if not client.is_ready():
        print("❌ Firebase not ready")
        return False
    
    try:
        # Clear test data
        database_url = client.database_url
        
        # Clear location data
        url = f"{database_url}user/location.json"
        response = requests.put(url, json=None, timeout=10)
        print("✅ Cleared location data")
        
        # Clear command data
        url = f"{database_url}user/command.json"
        response = requests.put(url, json=None, timeout=10)
        print("✅ Cleared command data")
        
        # Clear status data
        url = f"{database_url}system/router.json"
        response = requests.put(url, json=None, timeout=10)
        print("✅ Cleared router status")
        
        url = f"{database_url}system/client.json"
        response = requests.put(url, json=None, timeout=10)
        print("✅ Cleared client status")
        
        print("🎉 Firebase cleanup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up Firebase: {e}")
        return False

if __name__ == "__main__":
    cleanup_firebase()
