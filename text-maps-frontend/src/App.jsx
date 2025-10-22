/**
 * Text Maps Frontend - Accessible Navigation Application
 * 
 * This is the main React application component that provides accessible navigation
 * services with voice guidance support for visually impaired users. The app integrates
 * with the backend API to provide turn-by-turn directions, live navigation, and
 * comprehensive accessibility features.
 * 
 * Key Features:
 * - Voice-guided navigation with speech synthesis
 * - Speech-to-text input for hands-free operation
 * - Live navigation with real-time location tracking
 * - Multi-modal transportation support (walking, driving, cycling)
 * - Screen reader compatibility and accessibility features
 * - Error handling and user feedback
 */

import React, { useState, useEffect } from 'react';
import NavigationForm from './components/NavigationForm';
import RouteDisplay from './components/RouteDisplay';
import LiveNavigation from './components/LiveNavigation';
import Header from './components/Header';
import ErrorBoundary from './components/ErrorBoundary';
import useVoiceGuidance from './hooks/useVoiceGuidance';

/**
 * Main App component that orchestrates the entire navigation application.
 * 
 * This component manages the global application state including:
 * - Route data and navigation state
 * - Loading states and error handling
 * - Live navigation mode
 * - Voice guidance integration
 * 
 * The component provides a unified interface for all navigation features
 * and ensures accessibility compliance throughout the user experience.
 */
function App() {
  // Core application state management
  const [route, setRoute] = useState(null);                    // Current route data with directions
  const [isLoading, setIsLoading] = useState(false);          // Loading state for API calls
  const [error, setError] = useState(null);                   // Error messages for user feedback
  const [liveMode, setLiveMode] = useState(false);            // Live navigation mode toggle
  const [currentLocation, setCurrentLocation] = useState(null); // User's current GPS location
  
  // Shared voice guidance state for accessibility features
  const voiceGuidance = useVoiceGuidance();

  // Debug route state changes for development and troubleshooting
  useEffect(() => {
    console.log('Route state changed:', { route: !!route, liveMode, isLoading, error });
  }, [route, liveMode, isLoading, error]);

  /**
   * Handle route submission from the navigation form.
   * 
   * This function processes user input for route calculation, making API calls
   * to the backend service and managing loading states and error handling.
   * It provides comprehensive feedback to users and integrates with voice guidance.
   * 
   * @param {Object} formData - Route request data containing:
   *   - start_address (string): Starting location address
   *   - end_address (string): Destination address
   *   - mode (string): Transportation mode ('walking', 'driving', 'cycling')
   */
  const handleRouteSubmit = async (formData) => {
    console.log('handleRouteSubmit called with:', formData);
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Making API request to /api/directions...');
      const response = await fetch('/api/directions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      console.log('API response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('API error response:', errorData);
        throw new Error(errorData.error || 'Failed to get directions');
      }

      const data = await response.json();
      console.log('Route data received:', data);
      console.log('Setting route state...');
      setRoute({ ...data, mode: formData.mode });
      setLiveMode(false);
      console.log('Route state set successfully');
    } catch (err) {
      console.error('Route submission error:', err);
      setError(err.message);
    } finally {
      console.log('Setting loading to false');
      setIsLoading(false);
    }
  };

  /**
   * Handle live navigation mode with real-time location tracking.
   * 
   * This function initiates live navigation by getting the user's current location
   * and calculating a route to the destination. It provides real-time navigation
   * with voice guidance and location updates.
   * 
   * @param {Object} destination - Destination coordinates and address info
   * @param {number} destination.lat - Destination latitude
   * @param {number} destination.lng - Destination longitude
   * @param {string} destination.display_name - Human-readable destination name
   * @param {string} mode - Transportation mode for the route
   */
  const handleLiveNavigation = async (destination, mode) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get current location using browser geolocation API
      const position = await getCurrentPosition();
      const { latitude, longitude } = position.coords;
      
      setCurrentLocation({ lat: latitude, lng: longitude });
      
      // Get route to destination using current location as start point
      const response = await fetch('/api/route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_lat: latitude,
          start_lng: longitude,
          end_lat: destination.lat,
          end_lng: destination.lng,
          mode: mode
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get route');
      }

      const routeData = await response.json();
      setRoute({
        start: { lat: latitude, lng: longitude, display_name: 'Current Location' },
        end: destination,
        route: routeData,
        mode
      });
      setLiveMode(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Get current GPS position using browser geolocation API.
   * 
   * This function provides a Promise-based wrapper around the browser's
   * geolocation API with comprehensive error handling and accessibility
   * considerations for location access.
   * 
   * @returns {Promise<GeolocationPosition>} Promise resolving to position data
   * @throws {Error} If geolocation is not supported or access is denied
   */
  const getCurrentPosition = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => resolve(position),
        (error) => {
          let message = 'Unable to get your location';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              message = 'Location access denied. Please allow location access and try again.';
              break;
            case error.POSITION_UNAVAILABLE:
              message = 'Location information is unavailable.';
              break;
            case error.TIMEOUT:
              message = 'Location request timed out.';
              break;
          }
          reject(new Error(message));
        },
        {
          enableHighAccuracy: true,  // Request high accuracy for navigation
          timeout: 10000,           // 10 second timeout
          maximumAge: 0             // Don't use cached location
        }
      );
    });
  };

  /**
   * Clear current route and reset application state.
   * 
   * This function resets all navigation-related state to allow users
   * to start a new navigation session. It's called when users want to
   * clear their current route or start over.
   */
  const clearRoute = () => {
    console.log('Clearing route...');
    setRoute(null);
    setLiveMode(false);
    setCurrentLocation(null);
    setError(null);
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-900">
        <Header />
        
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <NavigationForm 
              onSubmit={handleRouteSubmit}
              onLiveNavigation={handleLiveNavigation}
              isLoading={isLoading}
              error={error}
              voiceGuidance={voiceGuidance}
            />
            
            {route && (
              <div className="mt-8">
                {liveMode ? (
                  <LiveNavigation 
                    route={route}
                    currentLocation={currentLocation}
                    onStop={() => setLiveMode(false)}
                    voiceGuidance={voiceGuidance}
                  />
                ) : (
                  <RouteDisplay 
                    route={route}
                    onClear={clearRoute}
                    voiceGuidance={voiceGuidance}
                  />
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
