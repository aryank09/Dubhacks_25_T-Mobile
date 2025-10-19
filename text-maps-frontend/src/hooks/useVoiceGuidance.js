import { useState, useEffect, useRef } from 'react';

const useVoiceGuidance = () => {
  const [isEnabled, setIsEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voice, setVoice] = useState(null);
  const [rate, setRate] = useState(1.0);
  const [pitch, setPitch] = useState(1.0);
  const [volume, setVolume] = useState(0.8);
  const synthRef = useRef(null);

  useEffect(() => {
    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      
      // Get available voices
      const loadVoices = () => {
        const voices = synthRef.current.getVoices();
        // Prefer English voices, especially those optimized for accessibility
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

      // Load voices when they become available
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

  const speak = (text, options = {}) => {
    console.log('speak called:', { isEnabled, text, hasSynth: !!synthRef.current, hasVoice: !!voice });
    
    if (!isEnabled || !synthRef.current || !voice) {
      console.log('speak: conditions not met');
      return;
    }

    // Cancel any ongoing speech
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.rate = options.rate || rate;
    utterance.pitch = options.pitch || pitch;
    utterance.volume = options.volume || volume;

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

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

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

  const announceTurnApproaching = (instruction, distanceToTurn) => {
    if (!isEnabled) return;

    if (distanceToTurn < 50) {
      speak(`Approaching turn: ${instruction}`, { rate: 0.8 });
    } else if (distanceToTurn < 100) {
      speak(`In ${Math.round(distanceToTurn)} meters: ${instruction}`, { rate: 0.9 });
    }
  };

  const announceError = (errorMessage) => {
    if (!isEnabled) return;
    speak(`Error: ${errorMessage}`, { rate: 0.7 });
  };

  const announceStatus = (status) => {
    console.log('announceStatus called:', { isEnabled, status });
    if (!isEnabled) {
      console.log('Voice guidance disabled, not speaking');
      return;
    }
    console.log('Speaking:', status);
    speak(status, { rate: 0.8 });
  };

  const readDirections = (directions) => {
    if (!isEnabled) return;
    
    // Split long text into chunks to avoid speech synthesis limits
    const maxLength = 200;
    const chunks = [];
    
    for (let i = 0; i < directions.length; i += maxLength) {
      chunks.push(directions.slice(i, i + maxLength));
    }
    
    // Read each chunk with a small delay
    chunks.forEach((chunk, index) => {
      setTimeout(() => {
        speak(chunk, { rate: 0.7 }); // Slower for better comprehension
      }, index * 2000); // 2 second delay between chunks
    });
  };

  const readStepByStep = (steps) => {
    if (!isEnabled || !steps || steps.length === 0) return;
    
    // Read each step with a pause between them
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
