#!/usr/bin/env python3
"""
System Test Script
Tests all components of the navigation assistant
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test if all required modules can be imported"""
    print("\n=== Testing Module Imports ===")
    
    modules = [
        ('voice_assistant', 'VoiceAssistant'),
        ('ai_brain', 'AIBrain'),
        ('navigation_system', 'NavigationSystem'),
        ('obstacle_detection', 'ObstacleDetector'),
        ('bluetooth_handler', 'BluetoothHandler'),
    ]
    
    failed = []
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            print(f"✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"✗ {module_name}.{class_name}: {e}")
            failed.append(module_name)
    
    return len(failed) == 0, failed


def test_voice_assistant():
    """Test voice assistant initialization"""
    print("\n=== Testing Voice Assistant ===")
    try:
        from voice_assistant import VoiceAssistant
        assistant = VoiceAssistant(use_gtts=False)
        print("✓ Voice assistant initialized")
        
        # Test TTS
        print("Testing text-to-speech...")
        assistant.speak("Testing voice assistant")
        print("✓ Text-to-speech working")
        
        return True
    except Exception as e:
        print(f"✗ Voice assistant test failed: {e}")
        return False


def test_ai_brain():
    """Test AI brain initialization"""
    print("\n=== Testing AI Brain ===")
    try:
        from ai_brain import AIBrain
        brain = AIBrain(service='openai')
        print("✓ AI brain initialized")
        
        # Test fallback response (works without API key)
        response = brain._fallback_response("Where am I?", None)
        print(f"✓ Fallback response: {response[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ AI brain test failed: {e}")
        return False


def test_navigation():
    """Test navigation system"""
    print("\n=== Testing Navigation System ===")
    try:
        from navigation_system import NavigationSystem
        nav = NavigationSystem()
        print("✓ Navigation system initialized")
        
        # Test geocoding
        print("Testing geocoding...")
        coords = nav.geocode_address("Space Needle, Seattle")
        if coords:
            print(f"✓ Geocoding working: {coords}")
        else:
            print("⚠ Geocoding requires internet connection")
        
        # Test distance calculation
        point1 = (47.6062, -122.3321)
        point2 = (47.6205, -122.3493)
        distance = nav.calculate_distance(point1, point2)
        print(f"✓ Distance calculation: {distance:.2f} meters")
        
        return True
    except Exception as e:
        print(f"✗ Navigation test failed: {e}")
        return False


def test_obstacle_detection():
    """Test obstacle detection"""
    print("\n=== Testing Obstacle Detection ===")
    try:
        from obstacle_detection import ObstacleDetector
        detector = ObstacleDetector(use_pi_camera=False)
        print("✓ Obstacle detector initialized")
        
        if detector.camera:
            print("✓ Camera available")
            # Try to capture a frame
            frame = detector.capture_frame()
            if frame is not None:
                print("✓ Camera capture working")
            else:
                print("⚠ Camera capture failed")
        else:
            print("⚠ No camera detected (this is OK for testing)")
        
        detector.cleanup()
        return True
    except Exception as e:
        print(f"✗ Obstacle detection test failed: {e}")
        return False


def test_bluetooth():
    """Test Bluetooth handler"""
    print("\n=== Testing Bluetooth Handler ===")
    try:
        from bluetooth_handler import BluetoothHandler
        bt = BluetoothHandler()
        print("✓ Bluetooth handler initialized")
        
        # Try to scan for devices
        print("Scanning for Bluetooth devices (this may take a few seconds)...")
        devices = bt.scan_devices(duration=3)
        print(f"✓ Found {len(devices)} Bluetooth device(s)")
        
        return True
    except Exception as e:
        print(f"⚠ Bluetooth test: {e}")
        print("  (Bluetooth may not be available on this system)")
        return True  # Don't fail on Bluetooth issues


def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n=== Checking Python Dependencies ===")
    
    dependencies = [
        'speech_recognition',
        'pyttsx3',
        'gtts',
        'geopy',
        'cv2',
        'numpy',
        'dotenv',
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} (missing)")
            missing.append(dep)
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 50)
    print("Navigation Assistant - System Test")
    print("=" * 50)
    
    results = {}
    
    # Check dependencies
    results['dependencies'] = check_dependencies()
    
    # Test imports
    results['imports'], failed = test_imports()
    
    # Test individual components
    if results['imports']:
        results['voice'] = test_voice_assistant()
        results['ai'] = test_ai_brain()
        results['navigation'] = test_navigation()
        results['obstacles'] = test_obstacle_detection()
        results['bluetooth'] = test_bluetooth()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name.upper()}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed!")
        print("\nYou can now run: python3 main.py")
    else:
        print("⚠ Some tests failed")
        print("\nPlease fix the issues before running the main application")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

