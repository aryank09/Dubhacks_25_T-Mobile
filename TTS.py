import ollama
import pyttsx3
import time
import speech_recognition as sr

# --- Part 1: Simple TTS function for basic text-to-speech ---
def say(text):
    """
    Simple function to speak text using TTS without Ollama.
    This is a lightweight function for basic text-to-speech needs.
    
    Args:
        text (str): The text to speak
        
    Returns:
        bool: True if successful, False if error occurred
    """
    try:
        # Initialize pyttsx3 TTS engine
        engine = pyttsx3.init()
        
        # Set properties (optional)
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Speak the text
        engine.say(text)
        engine.runAndWait()
        
        return True
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return False

# --- Part 2: Define the Ollama Text Generator ---
def get_ollama_response(prompt):
    """
    A generator function that yields text chunks (tokens) 
    from the local Ollama streaming API.
    """
    try:
        # Use ollama.chat with stream=True
        response = ollama.chat(
            model="gemma:2b", # Using the downloaded model
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        print("LLM: ", end="", flush=True)
        for chunk in response:
            token = chunk['message']['content']
            if token:
                print(token, end="", flush=True) # Print token to console
                yield token # Yield token to TTS
        print("\n") # Newline after LLM response is complete
    
    except Exception as e:
        print(f"\nError connecting to Ollama: {e}")
        print("Please ensure the Ollama application is running and you have pulled the model.")
        yield "An error occurred with Ollama."

# --- Part 3: Main TTS function for export ---
def speak_with_ollama(prompt):
    """
    Main function to handle TTS with Ollama integration.
    This function can be imported and called with a prompt.
    
    Args:
        prompt (str): The text prompt to send to Ollama
        
    Returns:
        bool: True if successful, False if error occurred
    """
    print("Initializing TTS engine (using pyttsx3)...")
    
    # Initialize pyttsx3 TTS engine
    engine = pyttsx3.init()
    
    # Set properties (optional)
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
    
    print(f"User: {prompt}\n")
    
    # Get the complete response from Ollama
    try:
        response_text = ""
        for token in get_ollama_response(prompt):
            response_text += token
        
        # Speak the complete response
        print(f"\nSpeaking: {response_text}")
        engine.say(response_text)
        engine.runAndWait()
        
        print("Playback finished.")
        return True
        
    except Exception as e:
        if "Connection refused" in str(e):
            print("\nFATAL ERROR: Could not connect to Ollama.")
            print("Please make sure the Ollama application is running.")
        else:
            print(f"An unexpected error occurred: {e}")
        return False

# --- Part 4: Speech Recognition Functions ---
def listen_for_input(timeout=10, phrase_time_limit=5):
    """
    Listen for voice input and return the recognized text.
    
    Args:
        timeout (int): Maximum time to wait for speech to start
        phrase_time_limit (int): Maximum time to listen for a complete phrase
        
    Returns:
        str: Recognized text, or None if no speech detected or error occurred
    """
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with microphone as source:
            print("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print(f"🎤 Listening for {timeout} seconds...")
        
        # Listen for audio
        with microphone as source:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        
        print("🎤 Processing speech...")
        
        # Recognize speech using Google's service
        text = recognizer.recognize_google(audio)
        print(f"🎤 Heard: {text}")
        return text.lower().strip()
        
    except sr.WaitTimeoutError:
        print("🎤 No speech detected within timeout period")
        return None
    except sr.UnknownValueError:
        print("🎤 Could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"🎤 Speech recognition service error: {e}")
        return None
    except Exception as e:
        print(f"🎤 Unexpected error: {e}")
        return None

def get_yes_no_confirmation(question, timeout=10):
    """
    Ask a yes/no question and get voice confirmation.
    
    Args:
        question (str): The question to ask
        timeout (int): Maximum time to wait for response
        
    Returns:
        bool: True for yes, False for no, None if no valid response
    """
    # Speak the question
    say(question)
    
    # Listen for response
    response = listen_for_input(timeout=timeout, phrase_time_limit=3)
    
    if response is None:
        return None
    
    # Check for yes/no responses
    yes_words = ['yes', 'yeah', 'yep', 'yup', 'correct', 'right', 'true', 'ok', 'okay']
    no_words = ['no', 'nope', 'nah', 'incorrect', 'wrong', 'false', 'not']
    
    if any(word in response for word in yes_words):
        return True
    elif any(word in response for word in no_words):
        return False
    else:
        print(f"🎤 Unclear response: '{response}'. Please say 'yes' or 'no'.")
        return None

# --- Part 5: Legacy main function for testing ---
# def main():
#     # Define your prompt
#     prompt = "In three short sentences, explain why the sky is blue."
    
#     # Call the main function
#     speak_with_ollama(prompt)

