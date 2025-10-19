import React, { useState, useEffect } from 'react';
import NavigationForm from './components/NavigationForm';
import RouteDisplay from './components/RouteDisplay';
import LiveNavigation from './components/LiveNavigation';
import Header from './components/Header';
import ErrorBoundary from './components/ErrorBoundary';
import useVoiceGuidance from './hooks/useVoiceGuidance';

function App() {
  const [route, setRoute] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [liveMode, setLiveMode] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  
  // Shared voice guidance state
  const voiceGuidance = useVoiceGuidance();

  // Debug route state changes
  useEffect(() => {
    console.log('Route state changed:', { route: !!route, liveMode, isLoading, error });
  }, [route, liveMode, isLoading, error]);

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
      setRoute(data);
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

  const handleLiveNavigation = async (destination, mode) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get current location
      const position = await getCurrentPosition();
      const { latitude, longitude } = position.coords;
      
      setCurrentLocation({ lat: latitude, lng: longitude });
      
      // Get route to destination
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
        route: routeData
      });
      setLiveMode(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

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
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    });
  };

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
