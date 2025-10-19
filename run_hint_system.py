#!/usr/bin/env python3
"""
HINT System Launcher
Easy way to run the HINT Gateway system
"""

import sys
import subprocess
import time
import os

def print_banner():
    """Print system banner"""
    print("=" * 60)
    print("🌐 HINT GATEWAY SYSTEM LAUNCHER")
    print("=" * 60)
    print("Raspberry Pi Router: Runs full navigation with voice interaction")
    print("Laptop Client: Sends GPS coordinates to Firebase")
    print("=" * 60)

def run_pi_router():
    """Run the Pi Navigation Router"""
    print("\n🌐 Starting Pi Navigation Router...")
    print("This will run the full navigation program with voice interaction")
    print("Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([sys.executable, "pi_navigation_router.py"])
    except KeyboardInterrupt:
        print("\n🛑 Pi Router stopped")

def run_laptop_client():
    """Run the GPS Laptop Client"""
    print("\n📍 Starting GPS Laptop Client...")
    print("This will only send GPS coordinates to Firebase")
    print("Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([sys.executable, "gps_laptop_client.py"])
    except KeyboardInterrupt:
        print("\n🛑 Laptop Client stopped")

def main():
    """Main launcher function"""
    print_banner()
    
    print("\nWhat would you like to run?")
    print("1. Pi Navigation Router (Raspberry Pi)")
    print("2. GPS Laptop Client (Laptop)")
    print("3. Test Firebase connection")
    print("4. Clean up Firebase data")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                run_pi_router()
                break
            elif choice == "2":
                run_laptop_client()
                break
            elif choice == "3":
                print("\n🧪 Testing Firebase connection...")
                subprocess.run([sys.executable, "test_firebase.py"])
                break
            elif choice == "4":
                print("\n🧹 Cleaning up Firebase data...")
                subprocess.run([sys.executable, "cleanup_firebase.py"])
                break
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
