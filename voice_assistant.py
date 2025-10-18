#!/usr/bin/env python3
"""
Voice Assistant for Navigation
Handles speech recognition and text-to-speech with AI integration
"""

import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import os
import tempfile
import logging
from typing import Optional
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceAssistant:
    def __init__(self, use_gtts=False):
        """
        Initialize voice assistant
        Args:
            use_gtts: If True, use Google TTS (requires internet), else use pyttsx3 (offline)
        """
        self.recognizer = sr.Recognizer()
        self.use_gtts = use_gtts
        
        if not use_gtts:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            
            # Try to set a pleasant voice
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        
        self.microphone = None
        self._init_microphone()
    
    def _init_microphone(self):
        """Initialize the microphone"""
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Microphone initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize microphone: {e}")
            self.microphone = None
    
    def speak(self, text: str):
        """Convert text to speech and play it"""
        logger.info(f"Speaking: {text}")
        
        try:
            if self.use_gtts:
                # Use Google TTS (requires internet)
                tts = gTTS(text=text, lang='en', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    temp_file = fp.name
                    tts.save(temp_file)
                
                # Play the audio file
                subprocess.run(['mpg123', '-q', temp_file])
                os.unlink(temp_file)
            else:
                # Use pyttsx3 (offline)
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
    
    def listen(self, timeout=5, phrase_time_limit=10) -> Optional[str]:
        """
        Listen for voice input and convert to text
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum duration of the phrase
        Returns:
            Recognized text or None if recognition failed
        """
        if not self.microphone:
            logger.error("Microphone not available")
            return None
        
        try:
            with self.microphone as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            logger.info("Processing speech...")
            # Use Google Speech Recognition (requires internet)
            # For offline, you could use Vosk or other options
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            logger.info("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in listen: {e}")
            return None
    
    def listen_for_wake_word(self, wake_word="assistant", timeout=None):
        """
        Continuously listen for wake word
        Args:
            wake_word: The word to trigger active listening
            timeout: How long to listen before giving up (None for infinite)
        Returns:
            True if wake word detected, False otherwise
        """
        if not self.microphone:
            return False
        
        try:
            with self.microphone as source:
                logger.info(f"Listening for wake word: '{wake_word}'")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=3
                )
            
            text = self.recognizer.recognize_google(audio).lower()
            if wake_word.lower() in text:
                logger.info("Wake word detected!")
                return True
            return False
            
        except Exception as e:
            logger.debug(f"Wake word detection: {e}")
            return False


if __name__ == "__main__":
    # Test voice assistant
    assistant = VoiceAssistant(use_gtts=False)
    
    assistant.speak("Hello! I am your navigation assistant. How can I help you today?")
    
    print("Say something...")
    text = assistant.listen()
    if text:
        print(f"You said: {text}")
        assistant.speak(f"You said: {text}")

