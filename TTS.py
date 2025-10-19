import ollama
import pyttsx3
import time

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

# --- Part 4: Legacy main function for testing ---
def main():
    # Define your prompt
    prompt = "In three short sentences, explain why the sky is blue."
    
    # Call the main function
    speak_with_ollama(prompt)

if __name__ == "__main__":
    main()