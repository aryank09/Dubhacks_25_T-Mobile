#!/usr/bin/env python3
"""
GPS System Setup Helper
Helps set up the computer-to-Raspberry Pi GPS system
"""

import subprocess
import sys
import time
import requests
from typing import Optional


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['requests', 'geocoder', 'flask', 'pyttsx3', 'pyaudio', 'SpeechRecognition']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True


def test_server_connection(server_url: str = "http://localhost:5000") -> bool:
    """Test connection to GPS server"""
    try:
        response = requests.get(f"{server_url}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is running")
            print(f"📍 Has location: {data.get('has_location', False)}")
            if data.get('age_seconds'):
                print(f"⏰ Location age: {data['age_seconds']:.1f} seconds")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {server_url}")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("🚀 GPS SYSTEM SETUP")
    print("="*60 + "\n")
    
    print("This script helps set up the computer-to-Raspberry Pi GPS system.")
    print("\nSetup involves:")
    print("1. Computer: Run gps_sender.py to send GPS coordinates")
    print("2. Raspberry Pi: Run gps_server.py to receive coordinates")
    print("3. Raspberry Pi: Run main.py --server-gps for navigation")
    
    print("\n" + "="*60)
    print("STEP 1: CHECK DEPENDENCIES")
    print("="*60)
    
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    print("\n" + "="*60)
    print("STEP 2: CHOOSE YOUR ROLE")
    print("="*60)
    
    print("\nAre you setting up:")
    print("1. Computer (sends GPS coordinates)")
    print("2. Raspberry Pi (receives GPS and runs navigation)")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == "1":
            setup_computer()
            break
        elif choice == "2":
            setup_raspberry_pi()
            break
        else:
            print("❌ Please enter 1 or 2")


def setup_computer():
    """Setup instructions for computer"""
    print("\n" + "="*60)
    print("🖥️  COMPUTER SETUP")
    print("="*60)
    
    print("\nTo send GPS coordinates from your computer:")
    print("\n1. Make sure the Raspberry Pi GPS server is running")
    print("2. Run the GPS sender:")
    print("   python gps_sender.py")
    print("\n   Or with custom server URL:")
    print("   python gps_sender.py http://RASPBERRY_PI_IP:5000")
    
    print("\n📝 Notes:")
    print("- The script will open a browser to get your GPS location")
    print("- Allow location access when prompted")
    print("- The script will continuously send your location to the server")
    print("- Press Ctrl+C to stop")


def setup_raspberry_pi():
    """Setup instructions for Raspberry Pi"""
    print("\n" + "="*60)
    print("🍓 RASPBERRY PI SETUP")
    print("="*60)
    
    print("\nTo run the GPS server and navigation on Raspberry Pi:")
    print("\n1. Start the GPS server (in one terminal):")
    print("   python gps_server.py")
    
    print("\n2. Start navigation with server GPS (in another terminal):")
    print("   python main.py --server-gps")
    print("\n   Or with custom server URL:")
    print("   python main.py --server-gps --server-url http://localhost:5000")
    
    print("\n📝 Notes:")
    print("- The server will wait for GPS coordinates from the computer")
    print("- The navigation will use coordinates from the server")
    print("- Make sure both are running before starting navigation")
    
    print("\n" + "="*60)
    print("TESTING CONNECTION")
    print("="*60)
    
    # Test server connection
    server_url = input("\nEnter server URL (default: http://localhost:5000): ").strip()
    if not server_url:
        server_url = "http://localhost:5000"
    
    print(f"\n🔗 Testing connection to {server_url}...")
    if test_server_connection(server_url):
        print("✅ Server connection successful!")
    else:
        print("❌ Could not connect to server")
        print("Make sure the GPS server is running on the Raspberry Pi")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
