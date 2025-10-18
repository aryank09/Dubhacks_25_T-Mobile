#!/usr/bin/env python3
"""
Main Navigation Assistant Application
Integrates all components for blind navigation system
"""

import logging
import time
import sys
from typing import Optional
from dotenv import load_dotenv

from voice_assistant import VoiceAssistant
from ai_brain import AIBrain
from navigation_system import NavigationSystem
from obstacle_detection import ObstacleDetector
from bluetooth_handler import BluetoothHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NavigationAssistant:
    def __init__(self, use_bluetooth=True, use_camera=True):
        """
        Initialize the complete navigation assistant
        Args:
            use_bluetooth: Enable Bluetooth audio
            use_camera: Enable obstacle detection camera
        """
        logger.info("Initializing Navigation Assistant...")
        
        # Initialize components
        self.voice = VoiceAssistant(use_gtts=False)  # Use offline TTS
        self.ai = AIBrain(service='ollama')  # Local LLM - no API needed!
        self.navigation = NavigationSystem()
        
        # Optional components
        self.bluetooth = None
        self.obstacle_detector = None
        
        if use_bluetooth:
            self.bluetooth = BluetoothHandler()
            logger.info("Bluetooth handler initialized")
        
        if use_camera:
            try:
                self.obstacle_detector = ObstacleDetector(use_pi_camera=True)
                logger.info("Obstacle detector initialized")
            except Exception as e:
                logger.warning(f"Obstacle detection disabled: {e}")
                self.obstacle_detector = None
        
        # Assistant state
        self.running = False
        self.destination_set = False
        
        logger.info("Navigation Assistant ready!")
    
    def start(self):
        """Start the navigation assistant"""
        self.running = True
        
        # Welcome message
        welcome = "Hello! I am your navigation assistant. Say 'help' to learn what I can do, or just ask me anything."
        self.voice.speak(welcome)
        
        # Main loop
        try:
            while self.running:
                self.listen_and_respond()
                time.sleep(0.5)  # Brief pause between interactions
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop()
    
    def listen_and_respond(self):
        """Listen for user input and respond"""
        # Listen for user speech
        user_input = self.voice.listen(timeout=5, phrase_time_limit=10)
        
        if not user_input:
            return
        
        # Check for exit commands
        if any(word in user_input.lower() for word in ['exit', 'quit', 'goodbye', 'stop']):
            self.voice.speak("Goodbye! Stay safe.")
            self.running = False
            return
        
        # Gather context
        context = self.gather_context()
        
        # Process with AI
        response = self.ai.process_query(user_input, context)
        
        # Handle special commands
        response = self.handle_commands(user_input, response, context)
        
        # Speak response
        self.voice.speak(response)
    
    def gather_context(self) -> dict:
        """Gather current context (location, obstacles, etc.)"""
        context = {}
        
        # Get current location
        location = self.navigation.get_current_location()
        if location:
            address = self.navigation.reverse_geocode(location[0], location[1])
            if address:
                context['location'] = address
            context['coordinates'] = location
        
        # Get destination info
        if self.navigation.destination:
            instruction = self.navigation.get_navigation_instruction()
            if instruction:
                context['navigation'] = instruction
        
        # Get obstacle info
        if self.obstacle_detector:
            try:
                scene_description = self.obstacle_detector.describe_scene()
                context['scene'] = scene_description
            except Exception as e:
                logger.error(f"Error detecting obstacles: {e}")
        
        return context
    
    def handle_commands(self, user_input: str, response: str, context: dict) -> str:
        """Handle special navigation commands"""
        user_input_lower = user_input.lower()
        
        # Navigate to destination
        if 'navigate to' in user_input_lower or 'take me to' in user_input_lower:
            # Extract destination from user input
            destination = user_input_lower.split('to')[-1].strip()
            if self.navigation.set_destination(destination):
                instruction = self.navigation.get_navigation_instruction()
                return f"Setting destination to {destination}. {instruction}"
            else:
                return f"Sorry, I couldn't find {destination}. Please try again."
        
        # What's around me / where am I
        elif any(phrase in user_input_lower for phrase in ['where am i', 'my location', 'current location']):
            if 'location' in context:
                return f"You are at {context['location']}"
            else:
                return "I'm trying to determine your location. Please ensure GPS is enabled."
        
        # What's ahead / obstacles
        elif any(phrase in user_input_lower for phrase in ['what\'s ahead', 'obstacles', 'in front']):
            if 'scene' in context:
                return context['scene']
            else:
                return "Camera is not available for obstacle detection."
        
        # Find nearby
        elif 'find' in user_input_lower or 'nearby' in user_input_lower:
            # Extract what to find
            query = user_input_lower.replace('find', '').replace('nearby', '').strip()
            if query:
                places = self.navigation.search_nearby(query)
                if places:
                    nearest = places[0]
                    distance = nearest['distance']
                    if distance < 1000:
                        dist_str = f"{int(distance)} meters"
                    else:
                        dist_str = f"{distance/1000:.1f} kilometers"
                    return f"The nearest {query} is {dist_str} away at {nearest['name']}"
                else:
                    return f"I couldn't find any {query} nearby."
        
        # Continue navigation
        elif any(phrase in user_input_lower for phrase in ['continue', 'keep going', 'next instruction']):
            if 'navigation' in context:
                return context['navigation']
            else:
                return "No destination set. Please tell me where you'd like to go."
        
        # Return AI response if no special command matched
        return response
    
    def stop(self):
        """Stop the assistant and cleanup"""
        self.running = False
        
        if self.obstacle_detector:
            self.obstacle_detector.cleanup()
        
        logger.info("Navigation Assistant stopped")


def main():
    """Main entry point"""
    # Parse command line arguments
    use_bluetooth = True
    use_camera = True
    
    if '--no-bluetooth' in sys.argv:
        use_bluetooth = False
    
    if '--no-camera' in sys.argv:
        use_camera = False
    
    # Create and start assistant
    assistant = NavigationAssistant(
        use_bluetooth=use_bluetooth,
        use_camera=use_camera
    )
    
    assistant.start()


if __name__ == "__main__":
    main()

