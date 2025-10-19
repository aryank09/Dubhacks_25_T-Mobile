#!/usr/bin/env python3
"""
Live TTS-enabled Walking Navigation
Provides real-time turn-by-turn voice directions using GPS updates every 5 seconds
"""

import sys
import time
import pyttsx3
from text_maps import TextMaps


class LiveVoiceNavigation:
    """Live navigation with TTS voice guidance"""
    
    def __init__(self):
        """Initialize the navigation system"""
        self.navigator = TextMaps()  # Permanently set to walking
        self.engine = None
        self.last_spoken_step = -1
        self.update_interval = 5  # Update every 5 seconds
        
    def init_tts(self):
        """Initialize TTS engine"""
        if not self.engine:
            print("🔊 Initializing TTS engine...")
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level
            print("✅ TTS engine ready\n")
    
    def speak(self, text: str, display: bool = True):
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
            display: Whether to display the text on screen
        """
        try:
            if display:
                print(f"\n🔊 SPEAKING: {text}\n")
            
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"⚠️  TTS Error: {e}")
    
    def format_instruction_for_speech(self, step: dict) -> str:
        """
        Format a navigation step for speech (no step numbers, natural language)
        
        Args:
            step: Navigation step dictionary
            
        Returns:
            Speech-friendly instruction text
        """
        maneuver = step['maneuver']
        distance = step['distance']
        direction_type = maneuver['type']
        modifier = maneuver.get('modifier', '')
        instruction = step.get('name', 'the road')
        
        # Format distance
        if distance < 1000:
            dist_text = f"{int(distance)} meters"
        else:
            km = distance / 1000
            dist_text = f"{km:.1f} kilometers"
        
        # Create natural speech instruction
        if direction_type == 'depart':
            return f"Head {modifier} on {instruction} for {dist_text}"
        elif direction_type == 'arrive':
            return "You have arrived at your destination"
        elif direction_type == 'turn':
            return f"In {dist_text}, turn {modifier} onto {instruction}"
        elif direction_type == 'merge':
            return f"In {dist_text}, merge {modifier} onto {instruction}"
        elif direction_type == 'roundabout':
            exit_num = maneuver.get('exit', 1)
            return f"In {dist_text}, at the roundabout, take exit {exit_num} onto {instruction}"
        elif direction_type == 'fork':
            return f"In {dist_text}, at the fork, keep {modifier} onto {instruction}"
        else:
            return f"In {dist_text}, {direction_type.replace('_', ' ')} {modifier} onto {instruction}"
    
    def run_live_navigation(self, destination: str):
        """
        Run live navigation with voice guidance
        
        Args:
            destination: Destination address
        """
        print(f"\n{'='*60}")
        print(f"🚶 🔊 LIVE VOICE-GUIDED WALKING NAVIGATION")
        print(f"{'='*60}")
        print(f"📍 Destination: {destination}")
        print(f"🔄 GPS Update Interval: {self.update_interval} seconds")
        print(f"{'='*60}\n")
        
        # Initialize TTS
        self.init_tts()
        
        # Get destination coordinates
        print("🔍 Finding destination...")
        dest_coords = self.navigator.geocode(destination)
        if not dest_coords:
            print(f"❌ Could not find destination: {destination}")
            self.speak(f"Error: Could not find destination {destination}")
            return
        
        print(f"✓ Destination: {dest_coords[0]:.4f}, {dest_coords[1]:.4f}\n")
        
        # Get initial location
        print("📍 Detecting your current location...")
        current_location = self.navigator.get_current_location()
        if not current_location:
            print("❌ Could not detect current location")
            self.speak("Error: Could not detect your current location")
            return
        
        print(f"✓ Current location: {current_location[0]:.4f}, {current_location[1]:.4f}\n")
        
        # Calculate initial route
        print("🗺️  Calculating route...\n")
        route_data = self.navigator.get_route(current_location, dest_coords)
        
        if not route_data or not route_data.get('routes'):
            print("❌ Could not find a route")
            self.speak("Error: Could not find a route to your destination")
            return
        
        route = route_data['routes'][0]
        steps = route['legs'][0]['steps']
        total_distance = route['distance']
        total_duration = route['duration']
        
        # Announce route summary
        print(f"{'='*60}")
        print(f"📊 ROUTE OVERVIEW")
        print(f"{'='*60}")
        print(f"Total Distance: {self.navigator.format_distance(total_distance)}")
        print(f"Estimated Time: {self.navigator.format_duration(total_duration)}")
        print(f"Total Steps: {len(steps)}")
        print(f"{'='*60}\n")
        
        summary = f"Route calculated. Total distance is {self.navigator.format_distance(total_distance)}. Estimated time is {self.navigator.format_duration(total_duration)}. Starting navigation."
        self.speak(summary)
        
        print("🚶 Starting live navigation...")
        print("Press Ctrl+C to stop\n")
        print(f"{'='*60}\n")
        
        current_step_idx = 0
        self.last_spoken_step = -1
        
        try:
            iteration = 0
            while current_step_idx < len(steps):
                iteration += 1
                
                # Get fresh GPS location
                print(f"\n🔄 Update #{iteration} - Getting current location...")
                current_location = self.navigator.get_current_location()
                if not current_location:
                    print("⚠️  Could not update location, retrying...")
                    time.sleep(self.update_interval)
                    continue
                
                # Calculate distance to destination
                distance_to_dest = self.navigator.calculate_distance(current_location, dest_coords)
                
                # Check if we've arrived (within 20 meters)
                if distance_to_dest < 20:
                    print("\n" + "="*60)
                    print("🎯 YOU HAVE ARRIVED AT YOUR DESTINATION!")
                    print("="*60 + "\n")
                    self.speak("You have arrived at your destination!")
                    break
                
                # Find current step based on location
                current_step_idx = self.navigator.find_current_step(current_location, steps)
                
                # Get current step
                step = steps[current_step_idx]
                
                # Calculate distance to next maneuver
                maneuver_location = step['maneuver']['location']
                maneuver_coords = (maneuver_location[1], maneuver_location[0])
                distance_to_maneuver = self.navigator.calculate_distance(current_location, maneuver_coords)
                
                # Display current status
                print("\n" + "="*60)
                print(f"📍 Current Position: {current_location[0]:.4f}, {current_location[1]:.4f}")
                print(f"📏 Distance to destination: {self.navigator.format_distance(distance_to_dest)}")
                print(f"📏 Distance to next turn: {self.navigator.format_distance(distance_to_maneuver)}")
                print(f"\n🧭 CURRENT INSTRUCTION (Step {current_step_idx + 1}/{len(steps)}):")
                
                instruction_text = self.format_instruction_for_speech(step)
                print(f"   {instruction_text}")
                
                # Speak instruction if:
                # 1. We moved to a new step, OR
                # 2. We're close to the maneuver (within 50 meters) and haven't spoken this step yet
                should_speak = False
                if current_step_idx != self.last_spoken_step:
                    should_speak = True
                    if self.last_spoken_step != -1:
                        print(f"\n✅ Completed step {self.last_spoken_step + 1}! Moving to step {current_step_idx + 1}")
                
                if should_speak:
                    self.speak(instruction_text)
                    self.last_spoken_step = current_step_idx
                
                # Show next instruction if available
                if current_step_idx + 1 < len(steps):
                    next_step = steps[current_step_idx + 1]
                    next_instruction = self.format_instruction_for_speech(next_step)
                    print(f"\n⏭️  NEXT:")
                    print(f"   {next_instruction}")
                
                print("="*60)
                
                # Wait before next update
                print(f"\n⏳ Next update in {self.update_interval} seconds... (Press Ctrl+C to stop)")
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Navigation stopped by user")
            print(f"Last known position: {current_location[0]:.4f}, {current_location[1]:.4f}\n")
            self.speak("Navigation stopped")


def main():
    """Main function to run live voice navigation"""
    print("\n" + "="*60)
    print("🚶 🔊 LIVE VOICE-GUIDED WALKING NAVIGATION")
    print("="*60 + "\n")
    
    # Get destination
    args = sys.argv[1:]
    
    if len(args) >= 1:
        # Use command line argument
        destination = args[0]
    else:
        # Interactive mode
        print("Enter your destination:\n")
        destination = input("Destination: ").strip()
        if not destination:
            print("❌ Destination cannot be empty")
            return
    
    # Create navigation system and run
    nav_system = LiveVoiceNavigation()
    nav_system.run_live_navigation(destination)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Navigation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
