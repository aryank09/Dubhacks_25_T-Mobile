#!/usr/bin/env python3
"""
Test script for voice confirmation functionality
"""

from TTS import get_yes_no_confirmation, listen_for_input, say

def test_voice_confirmation():
    """Test the voice confirmation functionality"""
    print("🎤 Testing Voice Confirmation Functionality")
    print("="*50)
    
    # Test 1: Yes/No confirmation
    print("\n1. Testing yes/no confirmation...")
    print("The system will ask you a question and wait for your voice response.")
    print("Please say 'yes' or 'no' when prompted.")
    
    response = get_yes_no_confirmation("Is this a test question? Please say yes or no.", timeout=10)
    
    if response is True:
        print("✅ You said YES")
    elif response is False:
        print("❌ You said NO")
    else:
        print("⚠️  No clear response received")
    
    # Test 2: General voice input
    print("\n2. Testing general voice input...")
    print("The system will ask you to say something and wait for your voice response.")
    
    say("Please say your name or any word you like.")
    text = listen_for_input(timeout=10, phrase_time_limit=5)
    
    if text:
        print(f"✅ You said: '{text}'")
    else:
        print("⚠️  No speech detected")
    
    print("\n🎉 Voice confirmation test completed!")

if __name__ == "__main__":
    test_voice_confirmation()
