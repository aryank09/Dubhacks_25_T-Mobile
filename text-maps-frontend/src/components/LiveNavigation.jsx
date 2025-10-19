import React, { useState, useEffect, useRef } from 'react';

const LiveNavigation = ({ route, currentLocation, onStop, voiceGuidance }) => {
  const { 
    isEnabled, 
    announceNavigation, 
    announceTurnApproaching,
    announceStatus,
    stopSpeaking 
  } = voiceGuidance;
  const [currentStep, setCurrentStep] = useState(0);
  const [distanceToDestination, setDistanceToDestination] = useState(null);
  const [distanceToNextTurn, setDistanceToNextTurn] = useState(null);
  const [isNavigating, setIsNavigating] = useState(true);
  const [locationError, setLocationError] = useState(null);
  const watchId = useRef(null);

  const formatDistance = (meters) => {
    if (meters < 1000) {
      return `${Math.round(meters)}m`;
    }
    return `${(meters / 1000).toFixed(1)}km`;
  };

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c; // Distance in meters
  };

  const updateLocation = (position) => {
    const { latitude, longitude } = position.coords;
    
    // Calculate distance to destination
    const destDistance = calculateDistance(
      latitude, longitude,
      route.end.lat, route.end.lng
    );
    setDistanceToDestination(destDistance);

    // Check if arrived (within 20 meters)
    if (destDistance < 20) {
      setIsNavigating(false);
      setCurrentStep(route.route.steps.length - 1);
      if (isEnabled) {
        announceNavigation("You have arrived at your destination", route.route.steps.length, 0, true);
      }
      return;
    }

    // Find closest step
    let closestStep = 0;
    let minDistance = Infinity;

    route.route.steps.forEach((step, index) => {
      const stepDistance = calculateDistance(
        latitude, longitude,
        step.coordinates[1], step.coordinates[0]
      );
      
      if (stepDistance < minDistance) {
        minDistance = stepDistance;
        closestStep = index;
      }
    });

    setCurrentStep(closestStep);
    
    // Calculate distance to next turn
    if (closestStep < route.route.steps.length - 1) {
      const nextStep = route.route.steps[closestStep + 1];
      const nextTurnDistance = calculateDistance(
        latitude, longitude,
        nextStep.coordinates[1], nextStep.coordinates[0]
      );
      setDistanceToNextTurn(nextTurnDistance);
      
      // Announce approaching turn
      if (isEnabled && nextTurnDistance < 100) {
        announceTurnApproaching(nextStep.instruction, nextTurnDistance);
      }
    } else {
      setDistanceToNextTurn(0);
    }
  };

  const handleLocationError = (error) => {
    let message = 'Unable to get your location';
    switch (error.code) {
      case error.PERMISSION_DENIED:
        message = 'Location access denied. Please allow location access.';
        break;
      case error.POSITION_UNAVAILABLE:
        message = 'Location information is unavailable.';
        break;
      case error.TIMEOUT:
        message = 'Location request timed out.';
        break;
    }
    setLocationError(message);
  };

  useEffect(() => {
    if (isNavigating) {
      // Start watching location
      if (navigator.geolocation) {
        watchId.current = navigator.geolocation.watchPosition(
          updateLocation,
          handleLocationError,
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 5000
          }
        );
      } else {
        setLocationError('Geolocation is not supported by this browser');
      }
    }

    return () => {
      if (watchId.current) {
        navigator.geolocation.clearWatch(watchId.current);
      }
    };
  }, [isNavigating]);

  const getStepIcon = (step, index, totalSteps) => {
    if (index === 0) {
      return '🚗';
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

  const currentStepData = route.route.steps[currentStep];
  const nextStepData = currentStep < route.route.steps.length - 1 
    ? route.route.steps[currentStep + 1] 
    : null;

  return (
    <div className="terminal">
      <div className="terminal-header">
        <div className="terminal-dot terminal-dot-red"></div>
        <div className="terminal-dot terminal-dot-yellow"></div>
        <div className="terminal-dot terminal-dot-green"></div>
        <span className="text-green-400 font-semibold">Live Navigation</span>
        <div className="ml-auto flex items-center gap-2">
          {isEnabled && (
            <button
              onClick={() => {
                stopSpeaking();
                announceStatus('Live navigation stopped');
              }}
              className="text-blue-400 hover:text-blue-300 transition-colors text-sm"
              aria-label="Stop voice guidance"
            >
              🔇 Stop Voice
            </button>
          )}
          <button
            onClick={onStop}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Stop live navigation"
          >
            ⏹️ Stop
          </button>
        </div>
      </div>

      {locationError ? (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-400">
            <span>❌</span>
            <span className="font-semibold">Location Error:</span>
          </div>
          <p className="text-red-300 mt-1">{locationError}</p>
        </div>
      ) : (
        <>
          {/* Current Status */}
          <div className="route-summary">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {distanceToDestination ? formatDistance(distanceToDestination) : '--'}
                </div>
                <div className="text-sm text-gray-400">To Destination</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">
                  {distanceToNextTurn ? formatDistance(distanceToNextTurn) : '--'}
                </div>
                <div className="text-sm text-gray-400">To Next Turn</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">
                  {currentStep + 1} / {route.route.steps.length}
                </div>
                <div className="text-sm text-gray-400">Current Step</div>
              </div>
            </div>
          </div>

          {/* Current Instruction */}
          {currentStepData && (
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-6 mb-4">
              <div className="flex items-center gap-4 mb-2">
                <span className="text-3xl">
                  {getStepIcon(currentStepData, currentStep, route.route.steps.length)}
                </span>
                <span className="direction-arrow text-3xl">{currentStepData.direction}</span>
                <div>
                  <div className="text-green-400 font-semibold text-lg">
                    CURRENT INSTRUCTION:
                  </div>
                  <div className="instruction text-xl">
                    {currentStepData.step}. {currentStepData.instruction}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Next Instruction */}
          {nextStepData && (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <span className="text-2xl">
                  {getStepIcon(nextStepData, currentStep + 1, route.route.steps.length)}
                </span>
                <span className="direction-arrow text-2xl">{nextStepData.direction}</span>
                <div>
                  <div className="text-gray-400 font-semibold text-sm">
                    NEXT:
                  </div>
                  <div className="instruction">
                    {nextStepData.step}. {nextStepData.instruction}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Arrival Message */}
          {!isNavigating && (
            <div className="mt-6 p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
              <div className="flex items-center gap-2 text-green-400 font-semibold text-lg">
                <span>🎉</span>
                <span>You have arrived at your destination!</span>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default LiveNavigation;
