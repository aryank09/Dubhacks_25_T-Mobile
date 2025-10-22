/**
 * RouteDisplay - Route Results and Turn-by-Turn Directions Component
 * 
 * This component displays the calculated route with comprehensive turn-by-turn
 * directions, route summary information, and voice guidance integration.
 * It provides accessibility features for visually impaired users including
 * voice announcements and step-by-step reading capabilities.
 * 
 * Key Features:
 * - Route summary with distance, duration, and step count
 * - Turn-by-turn directions with visual indicators
 * - Voice guidance integration for accessibility
 * - Step-by-step and continuous reading options
 * - Error handling for malformed route data
 * - Clear route functionality
 */

import React, { useEffect, useCallback } from 'react';
// remove local hook import
// import useVoiceGuidance from '../hooks/useVoiceGuidance';

/**
 * Route display component with voice guidance and accessibility features.
 * 
 * This component renders the complete route information including summary
 * statistics, turn-by-turn directions, and voice guidance controls. It
 * provides comprehensive accessibility features for visually impaired users.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.route - Route data containing start, end, and route information
 * @param {Function} props.onClear - Callback to clear the current route
 * @param {Object} props.voiceGuidance - Voice guidance controls and state
 */
const RouteDisplay = ({ route, onClear, voiceGuidance }) => {
  // Use the shared voiceGuidance object passed from App
  const {
    isEnabled = false,              // Voice guidance enabled status
    announceRouteStart = () => {}, // Announce route start
    announceNavigation = () => {}, // Announce navigation instructions
    announceStatus = () => {},     // Announce status messages
    readDirections = () => {},     // Read full directions
    readStepByStep = () => {}      // Read step-by-step directions
  } = voiceGuidance || {};

  const readAllDirections = useCallback(() => {
    console.log('readAllDirections called:', { route: !!route, isEnabled, steps: route?.route?.steps?.length });
    console.log('Speech synthesis available:', 'speechSynthesis' in window);
    console.log('Voice guidance enabled:', isEnabled);
    
    if (!route || !route.route || !route.route.steps) {
      console.log('readAllDirections: conditions not met');
      return;
    }
    
    // Stop any current speech to prevent interference
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
    }
    
    // Create a speech queue to prevent overlapping
    const speechQueue = route.route.steps.map((step, index) => {
      const distance = step.distance || 0;
      const distanceText = distance < 1000 ? 
        `${Math.round(distance)} meters` : 
        `${(distance / 1000).toFixed(1)} kilometers`;
      
      return `Step ${step.step || index + 1}. ${step.instruction || 'Continue'}. Distance: ${distanceText}.`;
    });
    
    // Speak each instruction sequentially
    let currentIndex = 0;
    const speakNext = () => {
      if (currentIndex < speechQueue.length) {
        const instruction = speechQueue[currentIndex];
        console.log('Reading step:', instruction);
        
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(instruction);
          utterance.rate = 0.8;
          utterance.pitch = 1;
          utterance.volume = 1;
          
          // When this utterance finishes, speak the next one
          utterance.onend = () => {
            currentIndex++;
            setTimeout(speakNext, 200); // Small delay between steps
          };
          
          utterance.onerror = () => {
            console.error('Speech synthesis error for:', instruction);
            currentIndex++;
            setTimeout(speakNext, 200);
          };
          
          speechSynthesis.speak(utterance);
        }
        
        currentIndex++;
      }
    };
    
    // Start the speech queue
    speakNext();
  }, [route, isEnabled, announceStatus]);

  // Announce route start and read all directions when route is loaded
  useEffect(() => {
    console.log('RouteDisplay useEffect triggered:', { 
      route: !!route, 
      isEnabled, 
      routeData: route ? {
        hasStart: !!route.start,
        hasEnd: !!route.end,
        hasRoute: !!route.route,
        stepsCount: route.route?.steps?.length
      } : null
    });

    if (route && isEnabled) {
      // Check if route has the expected structure
      if (!route.end || !route.route) {
        console.error('Route data is missing required fields:', route);
        return;
      }

      const destination = route.end?.display_name || 'Unknown destination';
      const totalDistance = route.route?.distance || 0;
      const estimatedTime = route.route?.duration || 0;

      console.log('Starting voice guidance for route:', { destination, totalDistance, estimatedTime });

      // Announce route start
      announceRouteStart && announceRouteStart(destination, totalDistance, estimatedTime);

      // Read directions immediately without any delay
      console.log('Starting to read directions immediately...');
      
      // Start reading directions immediately
      readAllDirections();
    } else if (route && !isEnabled) {
      console.log('Route loaded but voice disabled');
      // If voice is disabled, still read directions using browser speech synthesis
      console.log('Voice disabled, using browser speech synthesis...');
      readAllDirections();
    }
  }, [route, isEnabled, announceRouteStart, announceStatus, readAllDirections]);

  const readAllDirectionsContinuous = () => {
    if (!route || !route.route || !route.route.steps) return;
    
    const directions = route.route.steps.map((step, index) => {
      const distance = step.distance || 0;
      const distanceText = distance < 1000 ? 
        `${Math.round(distance)} meters` : 
        `${(distance / 1000).toFixed(1)} kilometers`;
      
      return `Step ${step.step || index + 1}. ${step.instruction || 'Continue'}. Distance: ${distanceText}.`;
    }).join(' ');
    
    // Try voice guidance first, then fallback to browser speech
    if (isEnabled && readDirections) {
      readDirections(directions);
    } else {
      // Fallback to browser speech synthesis
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(directions);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        speechSynthesis.speak(utterance);
      }
    }
  };
  const formatDistance = (meters) => {
    if (meters < 1000) {
      return `${Math.round(meters)}m`;
    }
    return `${(meters / 1000).toFixed(1)}km`;
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const getStepIcon = (step, index, totalSteps) => {
    const mode = route?.mode || 'walking';
    const startIcon = mode === 'walking' ? '🚶' : mode === 'cycling' ? '🚴' : '🚗';
    if (index === 0) {
      return startIcon;
    } else if (index === totalSteps - 1) {
      return '🏁';
    } else if (step.instruction.includes('Turn left')) {
      return '←';
    } else if (step.instruction.includes('Turn right')) {
      return '→';
    } else if (step.instruction.includes('Merge')) {
      return '⤴';
    } else if (step.instruction.includes('Continue')) {
      return '→';
    }
    return '→';
  };

  // Add error handling for malformed route data
  if (!route) {
    console.error('RouteDisplay: No route data provided');
    return null; // Don't render anything if no route
  }

  if (!route.route || !route.start || !route.end) {
    console.error('RouteDisplay: Invalid route data:', route);
    return (
      <div className="terminal">
        <div className="terminal-header">
          <div className="terminal-dot terminal-dot-red"></div>
          <div className="terminal-dot terminal-dot-yellow"></div>
          <div className="terminal-dot terminal-dot-green"></div>
          <span className="text-red-400 font-semibold">Route Error</span>
        </div>
        <div className="p-4 text-red-300">
          <p>Invalid route data received. Please try again.</p>
          <button
            onClick={onClear}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Clear and Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="terminal">
      <div className="terminal-header">
        <div className="terminal-dot terminal-dot-red"></div>
        <div className="terminal-dot terminal-dot-yellow"></div>
        <div className="terminal-dot terminal-dot-green"></div>
        <span className="text-green-400 font-semibold">Route Results</span>
        <div className="ml-auto flex items-center gap-2">
          {isEnabled && (
            <>
              <button
                onClick={() => {
                  console.log('Manual read button clicked');
                  readAllDirections();
                }}
                className="text-green-400 hover:text-green-300 transition-colors text-sm"
                aria-label="Read all directions step by step"
              >
                📖 Read Step by Step
              </button>
              <button
                onClick={readAllDirectionsContinuous}
                className="text-blue-400 hover:text-blue-300 transition-colors text-sm"
                aria-label="Read all directions continuously"
              >
                📚 Read All
              </button>
              <button
                onClick={() => announceStatus('Route cleared')}
                className="text-purple-400 hover:text-purple-300 transition-colors text-sm"
                aria-label="Announce route cleared"
              >
                🔊 Announce
              </button>
              <button
                onClick={() => {
                  if ('speechSynthesis' in window) {
                    const utterance = new SpeechSynthesisUtterance('Testing speech synthesis. This is a test of the voice reading system.');
                    utterance.rate = 0.9;
                    utterance.pitch = 1;
                    utterance.volume = 1;
                    speechSynthesis.speak(utterance);
                  }
                }}
                className="text-yellow-400 hover:text-yellow-300 transition-colors text-sm"
                aria-label="Test speech synthesis"
              >
                🧪 Test Voice
              </button>
              <button
                onClick={() => {
                  if ('speechSynthesis' in window) {
                    speechSynthesis.cancel();
                    console.log('Speech synthesis cancelled');
                  }
                }}
                className="text-red-400 hover:text-red-300 transition-colors text-sm"
                aria-label="Stop speech"
              >
                🛑 Stop Voice
              </button>
            </>
          )}
          <button
            onClick={onClear}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Clear route"
          >
            ✕ Clear
          </button>
        </div>
      </div>

      {/* Route Summary */}
      <div className="route-summary">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {formatDistance(route.route?.distance || 0)}
            </div>
            <div className="text-sm text-gray-400">Total Distance</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {formatDuration(route.route?.duration || 0)}
            </div>
            <div className="text-sm text-gray-400">Estimated Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">
              {route.route?.steps?.length || 0}
            </div>
            <div className="text-sm text-gray-400">Steps</div>
          </div>
        </div>
        
        <div className="border-t border-gray-700 pt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">From:</span>
              <div className="text-gray-100 font-mono">{route.start.display_name}</div>
            </div>
            <div>
              <span className="text-gray-400">To:</span>
              <div className="text-gray-100 font-mono">{route.end.display_name}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Turn-by-Turn Directions */}
      <div className="space-y-3">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-green-400 font-bold text-lg">
            🧭 Turn-by-Turn Directions
          </h3>
          {isEnabled && (
            <div className="flex items-center gap-2 text-blue-400 text-sm">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
              <span>Voice guidance active</span>
            </div>
          )}
        </div>
        
        {(route.route?.steps || []).map((step, index) => (
          <div
            key={index}
            className="flex items-start gap-4 p-4 bg-gray-800 rounded-lg border border-gray-700"
          >
            <div className="flex-shrink-0">
              <div className="step-number">
                {step.step}
              </div>
            </div>
            
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">
                  {getStepIcon(step, index, route.route?.steps?.length || 0)}
                </span>
                <span className="direction-arrow">{step.direction}</span>
                <span className="instruction text-lg">
                  {step.instruction}
                </span>
                {isEnabled && (
                  <button
                    onClick={() => announceNavigation(step.instruction, step.step, step.distance)}
                    className="ml-auto text-blue-400 hover:text-blue-300 transition-colors text-sm"
                    aria-label={`Announce step ${step.step}`}
                  >
                    🔊
                  </button>
                )}
              </div>
              
              <div className="flex gap-4 text-sm text-gray-400">
                <span className="distance">
                  📏 {formatDistance(step.distance)}
                </span>
                <span className="duration">
                  ⏱️ {formatDuration(step.duration)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Arrival Message */}
      <div className="mt-6 p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
        <div className="flex items-center gap-2 text-green-400 font-semibold">
          <span>✅</span>
          <span>You have arrived at your destination!</span>
        </div>
      </div>
    </div>
  );
};

export default RouteDisplay;
