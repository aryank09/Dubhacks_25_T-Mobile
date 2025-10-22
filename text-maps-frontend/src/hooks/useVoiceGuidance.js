/**
 * useVoiceGuidance - Custom React Hook for Voice Guidance System
 * 
 * This hook provides comprehensive voice guidance functionality for accessible navigation.
 * It manages speech synthesis, voice selection, and provides various announcement
 * functions optimized for visually impaired users.
 * 
 * Key Features:
 * - Speech synthesis with customizable voice settings
 * - Route announcements and turn-by-turn voice guidance
 * - Error and status announcements
 * - Voice selection with accessibility preferences
 * - Rate, pitch, and volume control
 * 
 * @returns {Object} Voice guidance interface with controls and announcement functions
 */

import { useState, useEffect, useRef } from 'react';

/**
 * Custom hook for managing voice guidance and speech synthesis.
 * 
 * This hook provides a comprehensive interface for voice guidance features
 * including speech synthesis, voice selection, and various announcement
 * functions optimized for accessibility.
 * 
 * @returns {Object} Voice guidance interface containing:
 *   - isEnabled: Boolean indicating if voice guidance is active
 *   - setIsEnabled: Function to toggle voice guidance on/off
 *   - isSpeaking: Boolean indicating if speech is currently active
 *   - voice: Selected voice object for speech synthesis
 *   - setVoice: Function to change the selected voice
 *   - rate: Speech rate (0.1 to 10)
 *   - setRate: Function to change speech rate
 *   - pitch: Speech pitch (0 to 2)
 *   - setPitch: Function to change speech pitch
 *   - volume: Speech volume (0 to 1)
 *   - setVolume: Function to change speech volume
 *   - speak: Function to speak custom text
 *   - stopSpeaking: Function to stop current speech
 *   - announceNavigation: Function for turn-by-turn announcements
 *   - announceRouteStart: Function for route start announcements
 *   - announceTurnApproaching: Function for approaching turn alerts
 *   - announceError: Function for error announcements
 *   - announceStatus: Function for status announcements
 *   - readDirections: Function for reading full directions
 *   - readStepByStep: Function for step-by-step reading
 */
const useVoiceGuidance = () => {
  // Voice guidance state management
  const [isEnabled, setIsEnabled] = useState(false);        // Voice guidance enabled/disabled
  const [isSpeaking, setIsSpeaking] = useState(false);      // Current speech status
  const [voice, setVoice] = useState(null);                  // Selected voice for synthesis
  const [rate, setRate] = useState(1.0);                    // Speech rate (0.1-10)
  const [pitch, setPitch] = useState(1.0);                  // Speech pitch (0-2)
  const [volume, setVolume] = useState(0.8);                 // Speech volume (0-1)
  const synthRef = useRef(null);                            // Reference to speech synthesis API

  useEffect(() => {
    // Initialize speech synthesis system
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      
      // Load and select optimal voice for accessibility
      const loadVoices = () => {
        const voices = synthRef.current.getVoices();
        // Prefer English voices optimized for accessibility and clarity
        const preferredVoices = voices.filter(voice => 
          voice.lang.startsWith('en') && 
          (voice.name.includes('Enhanced') || 
           voice.name.includes('Accessibility') ||
           voice.name.includes('High Quality'))
        );
        
        if (preferredVoices.length > 0) {
          setVoice(preferredVoices[0]);
        } else if (voices.length > 0) {
          setVoice(voices[0]);
        }
      };

      // Load voices when they become available (async in some browsers)
      if (synthRef.current.getVoices().length > 0) {
        loadVoices();
      } else {
        synthRef.current.addEventListener('voiceschanged', loadVoices);
      }
    }

    return () => {
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  /**
   * Speak text using the browser's speech synthesis API.
   * 
   * This function provides the core speech functionality with customizable
   * voice settings and comprehensive error handling. It's optimized for
   * accessibility and provides clear feedback to users.
   * 
   * @param {string} text - Text to be spoken
   * @param {Object} options - Speech options
   * @param {number} options.rate - Speech rate override (0.1-10)
   * @param {number} options.pitch - Speech pitch override (0-2)
   * @param {number} options.volume - Speech volume override (0-1)
   */
  const speak = (text, options = {}) => {
    console.log('speak called:', { isEnabled, text, hasSynth: !!synthRef.current, hasVoice: !!voice });
    
    if (!isEnabled || !synthRef.current || !voice) {
      console.log('speak: conditions not met');
      return;
    }

    // Cancel any ongoing speech to prevent overlap
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.rate = options.rate || rate;
    utterance.pitch = options.pitch || pitch;
    utterance.volume = options.volume || volume;

    // Speech event handlers for state management
    utterance.onstart = () => {
      console.log('Speech started');
      setIsSpeaking(true);
    };
    utterance.onend = () => {
      console.log('Speech ended');
      setIsSpeaking(false);
    };
    utterance.onerror = (error) => {
      console.log('Speech error:', error);
      setIsSpeaking(false);
    };

    console.log('Starting speech synthesis');
    synthRef.current.speak(utterance);
  };

  /**
   * Stop current speech synthesis.
   * 
   * This function immediately stops any ongoing speech and resets
   * the speaking state. It's useful for interrupting announcements
   * or clearing the speech queue.
   */
  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  /**
   * Announce navigation instructions with step and distance information.
   * 
   * This function provides turn-by-turn voice guidance with clear
   * step numbering and distance information, optimized for accessibility.
   * 
   * @param {string} instruction - The navigation instruction text
   * @param {number} stepNumber - Current step number in the route
   * @param {number} distance - Distance for this step in meters
   * @param {boolean} isArrival - Whether this is the arrival instruction
   */
  const announceNavigation = (instruction, stepNumber, distance, isArrival = false) => {
    if (!isEnabled) return;

    let announcement = '';
    
    if (isArrival) {
      announcement = `You have arrived at your destination. ${instruction}`;
    } else {
      const distanceText = distance < 1000 ? 
        `${Math.round(distance)} meters` : 
        `${(distance / 1000).toFixed(1)} kilometers`;
      
      announcement = `Step ${stepNumber}. ${instruction}. Distance: ${distanceText}`;
    }

    speak(announcement, { rate: 0.9 }); // Slightly slower for clarity
  };

  /**
   * Announce the start of a navigation route with summary information.
   * 
   * This function provides a comprehensive route overview including
   * destination, total distance, and estimated time for user orientation.
   * 
   * @param {string} destination - Destination name or address
   * @param {number} totalDistance - Total route distance in meters
   * @param {number} estimatedTime - Estimated travel time in seconds
   */
  const announceRouteStart = (destination, totalDistance, estimatedTime) => {
    if (!isEnabled) return;

    const distanceText = totalDistance < 1000 ? 
      `${Math.round(totalDistance)} meters` : 
      `${(totalDistance / 1000).toFixed(1)} kilometers`;
    
    const timeText = estimatedTime < 60 ? 
      `${Math.round(estimatedTime)} seconds` : 
      `${Math.round(estimatedTime / 60)} minutes`;

    const announcement = `Navigation started to ${destination}. Total distance: ${distanceText}. Estimated time: ${timeText}.`;
    speak(announcement);
  };

  /**
   * Announce approaching turns with distance-based alerts.
   * 
   * This function provides proximity-based turn alerts to help users
   * prepare for upcoming maneuvers, with different alert distances
   * for different turn types.
   * 
   * @param {string} instruction - The turn instruction text
   * @param {number} distanceToTurn - Distance to the turn in meters
   */
  const announceTurnApproaching = (instruction, distanceToTurn) => {
    if (!isEnabled) return;

    if (distanceToTurn < 50) {
      speak(`Approaching turn: ${instruction}`, { rate: 0.8 });
    } else if (distanceToTurn < 100) {
      speak(`In ${Math.round(distanceToTurn)} meters: ${instruction}`, { rate: 0.9 });
    }
  };

  /**
   * Announce error messages with clear, accessible formatting.
   * 
   * This function provides error announcements with slower speech
   * rate for better comprehension and accessibility.
   * 
   * @param {string} errorMessage - The error message to announce
   */
  const announceError = (errorMessage) => {
    if (!isEnabled) return;
    speak(`Error: ${errorMessage}`, { rate: 0.7 });
  };

  /**
   * Announce general status messages to users.
   * 
   * This function provides status updates with appropriate speech
   * rate for clear communication and user feedback.
   * 
   * @param {string} status - The status message to announce
   */
  const announceStatus = (status) => {
    console.log('announceStatus called:', { isEnabled, status });
    if (!isEnabled) {
      console.log('Voice guidance disabled, not speaking');
      return;
    }
    console.log('Speaking:', status);
    speak(status, { rate: 0.8 });
  };

  /**
   * Read full directions text with chunking for long content.
   * 
   * This function handles long direction text by splitting it into
   * manageable chunks and reading them sequentially with appropriate
   * delays for better comprehension.
   * 
   * @param {string} directions - Full directions text to be read
   */
  const readDirections = (directions) => {
    if (!isEnabled) return;
    
    // Split long text into chunks to avoid speech synthesis limits
    const maxLength = 200;
    const chunks = [];
    
    for (let i = 0; i < directions.length; i += maxLength) {
      chunks.push(directions.slice(i, i + maxLength));
    }
    
    // Read each chunk with a small delay for better comprehension
    chunks.forEach((chunk, index) => {
      setTimeout(() => {
        speak(chunk, { rate: 0.7 }); // Slower for better comprehension
      }, index * 2000); // 2 second delay between chunks
    });
  };

  /**
   * Read directions step by step with individual step announcements.
   * 
   * This function provides step-by-step reading of navigation instructions
   * with appropriate delays between steps for better user comprehension
   * and accessibility.
   * 
   * @param {Array} steps - Array of step objects with instruction and distance
   */
  const readStepByStep = (steps) => {
    if (!isEnabled || !steps || steps.length === 0) return;
    
    // Read each step with a pause between them for better comprehension
    steps.forEach((step, index) => {
      setTimeout(() => {
        const distanceText = step.distance < 1000 ? 
          `${Math.round(step.distance)} meters` : 
          `${(step.distance / 1000).toFixed(1)} kilometers`;
        
        const instruction = `Step ${step.step}. ${step.instruction}. Distance: ${distanceText}.`;
        speak(instruction, { rate: 0.7 });
      }, index * 4000); // 4 second delay between steps for better comprehension
    });
  };

  return {
    isEnabled,
    setIsEnabled,
    isSpeaking,
    voice,
    setVoice,
    rate,
    setRate,
    pitch,
    setPitch,
    volume,
    setVolume,
    speak,
    stopSpeaking,
    announceNavigation,
    announceRouteStart,
    announceTurnApproaching,
    announceError,
    announceStatus,
    readDirections,
    readStepByStep
  };
};

export default useVoiceGuidance;
