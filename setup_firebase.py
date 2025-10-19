#!/usr/bin/env python3
"""
Firebase Setup Helper for HINT Gateway System
Helps configure Firebase Realtime Database for the Pi Router and Laptop Client
"""

import json
import os
import webbrowser
from firebase_config import FirebaseConfig

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🔥 FIREBASE SETUP FOR HINT GATEWAY SYSTEM")
    print("=" * 60)
    print("This script will help you configure Firebase for your")
    print("Raspberry Pi Router and Laptop Client communication.")
    print("=" * 60)

def print_firebase_steps():
    """Print Firebase setup steps"""
    print("\n📋 FIREBASE SETUP STEPS:")
    print("1. Go to https://console.firebase.google.com/")
    print("2. Click 'Create a project' or select existing project")
    print("3. Enable 'Realtime Database' in the Database section")
    print("4. Set database rules to allow read/write (for testing):")
    print("   {")
    print("     \"rules\": {")
    print("       \".read\": true,")
    print("       \".write\": true")
    print("     }")
    print("   }")
    print("5. Go to Project Settings > General > Your apps")
    print("6. Click 'Add app' > Web app")
    print("7. Copy the Firebase configuration")
    print("8. Paste it into this script when prompted")

def get_firebase_config():
    """Get Firebase configuration from user"""
    print("\n🔧 FIREBASE CONFIGURATION")
    print("-" * 30)
    
    config = {}
    
    print("Enter your Firebase configuration values:")
    print("(Press Enter to skip any field)")
    
    config['apiKey'] = input("API Key: ").strip()
    config['authDomain'] = input("Auth Domain (project-id.firebaseapp.com): ").strip()
    config['databaseURL'] = input("Database URL (https://project-id-default-rtdb.firebaseio.com/): ").strip()
    config['projectId'] = input("Project ID: ").strip()
    config['storageBucket'] = input("Storage Bucket (project-id.appspot.com): ").strip()
    config['messagingSenderId'] = input("Messaging Sender ID: ").strip()
    config['appId'] = input("App ID: ").strip()
    
    return config

def validate_config(config):
    """Validate Firebase configuration"""
    required_fields = ['apiKey', 'authDomain', 'databaseURL', 'projectId']
    
    missing_fields = []
    for field in required_fields:
        if not config.get(field) or config[field] == f"your-{field.replace('Id', '-id').replace('Key', '-key')}-here":
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n❌ Missing required fields: {', '.join(missing_fields)}")
        return False
    
    return True

def save_config(config):
    """Save configuration to file"""
    try:
        with open('firebase_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Configuration saved to firebase_config.json")
        return True
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def test_connection(config):
    """Test Firebase connection"""
    try:
        from firebase_client import FirebaseClient
        
        # Create temporary config file
        temp_config = config.copy()
        with open('temp_firebase_config.json', 'w') as f:
            json.dump(temp_config, f, indent=2)
        
        # Test connection
        client = FirebaseClient('temp_firebase_config.json')
        
        if client.is_ready():
            print("✅ Firebase connection successful!")
            
            # Test sending a status update
            success = client.send_status_update("test", "connection_test", {
                "message": "Firebase setup test successful"
            })
            
            if success:
                print("✅ Test data sent successfully!")
            else:
                print("⚠️  Connection successful but failed to send test data")
            
            # Clean up temp file
            os.remove('temp_firebase_config.json')
            return True
        else:
            print("❌ Firebase connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check if config already exists
    if os.path.exists('firebase_config.json'):
        print("\n⚠️  Firebase configuration file already exists.")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print_firebase_steps()
    
    # Ask if user wants to open Firebase console
    open_console = input("\n🌐 Open Firebase Console in browser? (Y/n): ").strip().lower()
    if open_console != 'n':
        webbrowser.open('https://console.firebase.google.com/')
    
    input("\nPress Enter when you have your Firebase configuration ready...")
    
    # Get configuration
    config = get_firebase_config()
    
    # Validate configuration
    if not validate_config(config):
        print("\n❌ Configuration validation failed. Please try again.")
        return
    
    # Save configuration
    if not save_config(config):
        return
    
    # Test connection
    print("\n🧪 Testing Firebase connection...")
    if test_connection(config):
        print("\n🎉 Firebase setup completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python pi_router.py' on your Raspberry Pi")
        print("2. Run 'python laptop_client.py' on your laptop")
        print("3. The Pi will pull location data every 5 seconds")
        print("4. The laptop will send location data and listen for commands")
    else:
        print("\n❌ Firebase setup failed. Please check your configuration.")

if __name__ == "__main__":
    main()
