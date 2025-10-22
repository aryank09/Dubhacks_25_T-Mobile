/**
 * NavigationForm - Main Navigation Input Component
 * 
 * This component provides the primary interface for users to input navigation
 * requests with comprehensive accessibility features including voice input,
 * voice guidance controls, and multiple transportation modes.
 * 
 * Key Features:
 * - Voice input for hands-free address entry
 * - Live navigation mode with GPS integration
 * - Voice guidance controls and status
 * - Multi-modal transportation support
 * - Accessibility-optimized form controls
 * - Real-time speech recognition feedback
 */

import React, { useState } from 'react';
import useSpeechToText from '../hooks/useSpeechToText';

/**
 * Navigation form component with voice input and accessibility features.
 * 
 * This component provides a comprehensive navigation interface with voice
 * input capabilities, live navigation mode, and voice guidance integration.
 * It supports multiple transportation modes and provides real-time feedback
 * for accessibility.
 * 
 * @param {Object} props - Component props
 * @param {Function} props.onSubmit - Callback for regular route submission
 * @param {Function} props.onLiveNavigation - Callback for live navigation
 * @param {boolean} props.isLoading - Loading state indicator
 * @param {string} props.error - Error message to display
 * @param {Object} props.voiceGuidance - Voice guidance controls and state
 */
const NavigationForm = ({ onSubmit, onLiveNavigation, isLoading, error, voiceGuidance }) => {
  // Form state management
  const [formData, setFormData] = useState({
    start_address: '',    // Starting location address
    end_address: '',      // Destination address
    mode: 'walking'       // Transportation mode
  });
  const [liveDestination, setLiveDestination] = useState('');        // Live navigation destination
  const [liveMode, setLiveMode] = useState('walking');              // Live navigation mode
  const [activeVoiceField, setActiveVoiceField] = useState(null);   // Track which field is being filled by voice
  
  // Voice guidance integration
  const { 
    isEnabled,           // Voice guidance enabled status
    setIsEnabled,       // Toggle voice guidance
    announceError,       // Announce error messages
    announceStatus,     // Announce status updates
    isSpeaking          // Current speech status
  } = voiceGuidance;

  // Speech-to-text functionality
  const {
    isListening,
    transcript,
    isSupported,
    error: speechError,
    startListening,
    stopListening,
    clearTranscript
  } = useSpeechToText();

  const modes = [
    { value: 'walking', label: '🚶 Walking', description: 'Accessible pedestrian routes with sidewalks and crosswalks' },
    { value: 'driving', label: '🚗 Driving', description: 'Vehicle routes' },
    { value: 'cycling', label: '🚴 Cycling', description: 'Bicycle-friendly routes' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted with data:', formData);
    
    if (formData.start_address && formData.end_address) {
      console.log('Starting route calculation...');
      announceStatus('Calculating route...');
      
      try {
        await onSubmit(formData);
        console.log('Route calculation completed');
      } catch (error) {
        console.error('Route calculation failed:', error);
      }
    } else {
      console.log('Form validation failed - missing required fields');
    }
  };

  const handleLiveNavigation = async (e) => {
    e.preventDefault();
    if (liveDestination) {
      try {
        announceStatus('Starting live navigation...');
        // Geocode the destination
        const response = await fetch('/api/geocode', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ address: liveDestination }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to find destination');
        }

        const destination = await response.json();
        await onLiveNavigation(destination, liveMode);
      } catch (err) {
        console.error('Live navigation error:', err);
        announceError(err.message);
      }
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Voice input handlers
  const startVoiceInput = (fieldName) => {
    if (!isSupported) {
      announceError('Speech recognition is not supported in this browser');
      return;
    }
    
    setActiveVoiceField(fieldName);
    clearTranscript();
    startListening();
    announceStatus(`Listening for ${fieldName === 'start_address' ? 'starting location' : 'destination'}...`);
  };

  const stopVoiceInput = () => {
    stopListening();
    setActiveVoiceField(null);
  };

  // Apply transcript to the active field when speech recognition completes
  React.useEffect(() => {
    if (transcript && activeVoiceField && !isListening) {
      if (activeVoiceField === 'start_address') {
        setFormData(prev => ({ ...prev, start_address: transcript }));
      } else if (activeVoiceField === 'end_address') {
        setFormData(prev => ({ ...prev, end_address: transcript }));
      } else if (activeVoiceField === 'live_destination') {
        setLiveDestination(transcript);
      }
      setActiveVoiceField(null);
      clearTranscript();
    }
  }, [transcript, activeVoiceField, isListening]);

  return (
    <div className="space-y-6">
      {/* Voice Guidance Controls */}
      <div className="terminal">
        <div className="terminal-header">
          <div className="terminal-dot terminal-dot-red"></div>
          <div className="terminal-dot terminal-dot-yellow"></div>
          <div className="terminal-dot terminal-dot-green"></div>
          <span className="text-green-400 font-semibold">Voice Guidance Settings</span>
        </div>
        
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsEnabled(!isEnabled)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                isEnabled 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
              aria-label={isEnabled ? 'Disable voice guidance' : 'Enable voice guidance'}
            >
              {isEnabled ? '🔊 Voice On' : '🔇 Voice Off'}
            </button>
            
            {isSpeaking && (
              <div className="flex items-center gap-2 text-blue-400">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-sm">Speaking...</span>
              </div>
            )}
          </div>
          
          <div className="text-sm text-gray-400">
            Voice guidance provides audio instructions for navigation
          </div>
        </div>
        
        {isEnabled && (
          <div className="px-4 pb-4">
            <div className="text-sm text-gray-400 mb-2">Voice Guidance Features:</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-300">
              <div>• Automatic route announcements</div>
              <div>• Step-by-step voice instructions</div>
              <div>• Live navigation voice alerts</div>
              <div>• Error message announcements</div>
            </div>
          </div>
        )}
      </div>

      {/* Regular Navigation Form */}
      <div className="terminal">
        <div className="terminal-header">
          <div className="terminal-dot terminal-dot-red"></div>
          <div className="terminal-dot terminal-dot-yellow"></div>
          <div className="terminal-dot terminal-dot-green"></div>
          <span className="text-green-400 font-semibold">Navigation Terminal</span>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-green-400 font-semibold mb-2" htmlFor="start-address">
              📍 Starting Location:
            </label>
            <div className="flex gap-2">
              <input
                id="start-address"
                type="text"
                name="start_address"
                value={formData.start_address}
                onChange={handleInputChange}
                placeholder="Enter starting address or 'current' for current location"
                className="input-field flex-1"
                disabled={isLoading}
                aria-describedby="start-address-help"
              />
              <button
                type="button"
                onClick={() => startVoiceInput('start_address')}
                disabled={isLoading || !isSupported || isListening}
                className={`px-3 py-2 rounded-lg font-semibold transition-colors ${
                  isListening && activeVoiceField === 'start_address'
                    ? 'bg-red-600 text-white animate-pulse'
                    : isSupported
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                }`}
                aria-label="Start voice input for starting location"
              >
                {isListening && activeVoiceField === 'start_address' ? '🛑 Stop' : '🎤 Voice'}
              </button>
            </div>
            <div id="start-address-help" className="text-xs text-gray-400 mt-1">
              You can enter an address, landmark, or use 'current' for your current location
              {isSupported && ' • Click the microphone to speak your starting location'}
            </div>
            {isListening && activeVoiceField === 'start_address' && (
              <div className="mt-2 text-sm text-blue-400 flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span>Listening for starting location...</span>
                {transcript && <span className="text-gray-300">"{transcript}"</span>}
              </div>
            )}
          </div>
          
          <div>
            <label className="block text-green-400 font-semibold mb-2" htmlFor="end-address">
              🎯 Destination:
            </label>
            <div className="flex gap-2">
              <input
                id="end-address"
                type="text"
                name="end_address"
                value={formData.end_address}
                onChange={handleInputChange}
                placeholder="Enter destination address"
                className="input-field flex-1"
                disabled={isLoading}
                aria-describedby="end-address-help"
              />
              <button
                type="button"
                onClick={() => startVoiceInput('end_address')}
                disabled={isLoading || !isSupported || isListening}
                className={`px-3 py-2 rounded-lg font-semibold transition-colors ${
                  isListening && activeVoiceField === 'end_address'
                    ? 'bg-red-600 text-white animate-pulse'
                    : isSupported
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                }`}
                aria-label="Start voice input for destination"
              >
                {isListening && activeVoiceField === 'end_address' ? '🛑 Stop' : '🎤 Voice'}
              </button>
            </div>
            <div id="end-address-help" className="text-xs text-gray-400 mt-1">
              Enter the address or name of your destination
              {isSupported && ' • Click the microphone to speak your destination'}
            </div>
            {isListening && activeVoiceField === 'end_address' && (
              <div className="mt-2 text-sm text-blue-400 flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span>Listening for destination...</span>
                {transcript && <span className="text-gray-300">"{transcript}"</span>}
              </div>
            )}
          </div>
          
          <div>
            <label className="block text-green-400 font-semibold mb-2">
              🚶 Transportation Mode:
            </label>
            <div className="mode-selector">
              {modes.map(mode => (
                <button
                  key={mode.value}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, mode: mode.value }))}
                  className={`mode-btn ${formData.mode === mode.value ? 'active' : 'inactive'}`}
                  disabled={isLoading}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          </div>
          
          <button
            type="submit"
            disabled={isLoading || !formData.start_address || !formData.end_address}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '🔄 Calculating Route...' : '🗺️ Get Directions'}
          </button>
        </form>
      </div>

      {/* Live Navigation Form */}
      <div className="terminal">
        <div className="terminal-header">
          <div className="terminal-dot terminal-dot-red"></div>
          <div className="terminal-dot terminal-dot-yellow"></div>
          <div className="terminal-dot terminal-dot-green"></div>
          <span className="text-green-400 font-semibold">Live Navigation Terminal</span>
        </div>
        
        <form onSubmit={handleLiveNavigation} className="space-y-4">
          <div>
            <label className="block text-green-400 font-semibold mb-2" htmlFor="live-destination">
              🧭 Live Navigation to:
            </label>
            <div className="flex gap-2">
              <input
                id="live-destination"
                type="text"
                value={liveDestination}
                onChange={(e) => setLiveDestination(e.target.value)}
                placeholder="Enter destination for live navigation"
                className="input-field flex-1"
                disabled={isLoading}
                aria-describedby="live-destination-help"
              />
              <button
                type="button"
                onClick={() => startVoiceInput('live_destination')}
                disabled={isLoading || !isSupported || isListening}
                className={`px-3 py-2 rounded-lg font-semibold transition-colors ${
                  isListening && activeVoiceField === 'live_destination'
                    ? 'bg-red-600 text-white animate-pulse'
                    : isSupported
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                }`}
                aria-label="Start voice input for live navigation destination"
              >
                {isListening && activeVoiceField === 'live_destination' ? '🛑 Stop' : '🎤 Voice'}
              </button>
            </div>
            <div id="live-destination-help" className="text-xs text-gray-400 mt-1">
              Live navigation will track your location and provide real-time voice guidance
              {isSupported && ' • Click the microphone to speak your destination'}
            </div>
            {isListening && activeVoiceField === 'live_destination' && (
              <div className="mt-2 text-sm text-blue-400 flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span>Listening for live navigation destination...</span>
                {transcript && <span className="text-gray-300">"{transcript}"</span>}
              </div>
            )}
          </div>
          
          <div>
            <label className="block text-green-400 font-semibold mb-2">
              🚶 Mode:
            </label>
            <div className="mode-selector">
              {modes.map(mode => (
                <button
                  key={mode.value}
                  type="button"
                  onClick={() => setLiveMode(mode.value)}
                  className={`mode-btn ${liveMode === mode.value ? 'active' : 'inactive'}`}
                  disabled={isLoading}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          </div>
          
          <button
            type="submit"
            disabled={isLoading || !liveDestination}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '🔄 Starting Live Navigation...' : '🧭 Start Live Navigation'}
          </button>
        </form>
      </div>

      {(error || speechError) && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4" role="alert" aria-live="polite">
          <div className="flex items-center gap-2 text-red-400">
            <span>❌</span>
            <span className="font-semibold">Error:</span>
          </div>
          <p className="text-red-300 mt-1">{error || speechError}</p>
          {isEnabled && (
            <button
              onClick={() => announceError(error || speechError)}
              className="mt-2 text-sm text-blue-400 hover:text-blue-300 underline"
              aria-label="Announce error message"
            >
              🔊 Announce Error
            </button>
          )}
        </div>
      )}

      {/* Speech Recognition Support Notice */}
      {!isSupported && (
        <div className="bg-yellow-900/50 border border-yellow-500 rounded-lg p-4" role="alert">
          <div className="flex items-center gap-2 text-yellow-400">
            <span>⚠️</span>
            <span className="font-semibold">Speech Recognition Not Supported</span>
          </div>
          <p className="text-yellow-300 mt-1">
            Your browser doesn't support speech recognition. You can still type your addresses manually.
          </p>
        </div>
      )}
    </div>
  );
};

export default NavigationForm;
