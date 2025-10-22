/**
 * useSpeechToText - Custom React Hook for Speech Recognition
 * 
 * This hook provides speech-to-text functionality using the Web Speech API.
 * It enables hands-free input for navigation addresses and supports
 * accessibility features for users with visual impairments.
 * 
 * Key Features:
 * - Real-time speech recognition with interim results
 * - Cross-browser compatibility with fallback handling
 * - Error handling and user feedback
 * - Automatic cleanup and resource management
 * 
 * @returns {Object} Speech recognition interface with controls and state
 */

import { useState, useEffect, useRef } from 'react';

/**
 * Custom hook for managing speech-to-text functionality.
 * 
 * This hook provides a comprehensive interface for speech recognition
 * including real-time transcription, error handling, and browser
 * compatibility management.
 * 
 * @returns {Object} Speech recognition interface containing:
 *   - isListening: Boolean indicating if speech recognition is active
 *   - transcript: Current speech recognition transcript text
 *   - isSupported: Boolean indicating if speech recognition is supported
 *   - error: Current error message if any
 *   - startListening: Function to start speech recognition
 *   - stopListening: Function to stop speech recognition
 *   - clearTranscript: Function to clear the current transcript
 */
const useSpeechToText = () => {
  // Speech recognition state management
  const [isListening, setIsListening] = useState(false);      // Recognition active status
  const [transcript, setTranscript] = useState('');           // Current transcript text
  const [isSupported, setIsSupported] = useState(false);     // Browser support status
  const [error, setError] = useState(null);                   // Error messages
  const recognitionRef = useRef(null);                       // Reference to recognition instance

  useEffect(() => {
    // Check if speech recognition is supported in the current browser
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);

    if (SpeechRecognition) {
      // Initialize speech recognition with accessibility-optimized settings
      const recognition = new SpeechRecognition();
      recognition.continuous = false;        // Single recognition session
      recognition.interimResults = true;     // Show interim results for real-time feedback
      recognition.lang = 'en-US';            // English language recognition

      // Speech recognition event handlers
      recognition.onstart = () => {
        setIsListening(true);
        setError(null);
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        // Process both final and interim results for real-time feedback
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscript(finalTranscript || interimTranscript);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setError(`Speech recognition error: ${event.error}`);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    // Cleanup function to stop recognition when component unmounts
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  /**
   * Start speech recognition session.
   * 
   * This function initiates a new speech recognition session,
   * clearing any previous transcript and error states.
   */
  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      setError(null);
      recognitionRef.current.start();
    }
  };

  /**
   * Stop current speech recognition session.
   * 
   * This function stops the active speech recognition session
   * and triggers the onend event handler.
   */
  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  /**
   * Clear current transcript and error states.
   * 
   * This function resets the transcript text and clears any
   * error messages, preparing for a new recognition session.
   */
  const clearTranscript = () => {
    setTranscript('');
    setError(null);
  };

  return {
    isListening,
    transcript,
    isSupported,
    error,
    startListening,
    stopListening,
    clearTranscript
  };
};

export default useSpeechToText;
