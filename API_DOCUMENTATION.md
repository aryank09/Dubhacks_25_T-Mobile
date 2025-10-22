# Text Maps API Documentation

## Overview

This document provides comprehensive documentation for the Text Maps accessible navigation API, including data structures, API endpoints, and response formats.

## API Base URL

- Development: `http://localhost:5000`
- Production: `https://your-domain.com`

## Authentication

No authentication required for basic usage. All endpoints are publicly accessible.

## Data Structures

### Geocoding Response

```typescript
interface GeocodingResult {
  lat: number;                    // Latitude coordinate
  lng: number;                    // Longitude coordinate
  display_name: string;           // Full formatted address
  address: {                     // Structured address components
    house_number?: string;
    road?: string;
    city?: string;
    state?: string;
    country?: string;
    postcode?: string;
  };
}
```

### Route Step

```typescript
interface RouteStep {
  step: number;                   // Step number in sequence
  instruction: string;            // Human-readable instruction
  distance: number;               // Distance in meters
  duration: number;               // Duration in seconds
  direction: string;              // Unicode direction arrow (↑, →, ↓, ←, etc.)
  coordinates: [number, number];  // [longitude, latitude] coordinates
}
```

### Route Geometry

```typescript
interface RouteGeometry {
  type: "LineString";
  coordinates: [number, number][]; // Array of [longitude, latitude] pairs
}
```

### Complete Route

```typescript
interface Route {
  distance: number;               // Total distance in meters
  duration: number;               // Total duration in seconds
  steps: RouteStep[];             // Turn-by-turn directions
  geometry: RouteGeometry;       // Route path geometry
}
```

### Full Directions Response

```typescript
interface DirectionsResponse {
  start: GeocodingResult;         // Starting location
  end: GeocodingResult;           // Destination location
  route: Route;                   // Complete route data
}
```

## API Endpoints

### 1. Geocode Address

**Endpoint:** `POST /api/geocode`

**Description:** Convert human-readable addresses to geographic coordinates.

**Request Body:**
```json
{
  "address": "123 Main St, Seattle, WA"
}
```

**Response:**
```json
{
  "lat": 47.6062,
  "lng": -122.3321,
  "display_name": "123 Main St, Seattle, WA 98101, USA",
  "address": {
    "house_number": "123",
    "road": "Main St",
    "city": "Seattle",
    "state": "Washington",
    "country": "United States",
    "postcode": "98101"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing address or geocoding failed
- `500 Internal Server Error`: Server error

### 2. Get Route

**Endpoint:** `POST /api/route`

**Description:** Get route between two geographic coordinates.

**Request Body:**
```json
{
  "start_lat": 47.6062,
  "start_lng": -122.3321,
  "end_lat": 47.6205,
  "end_lng": -122.3493,
  "mode": "walking"
}
```

**Parameters:**
- `start_lat` (required): Starting latitude
- `start_lng` (required): Starting longitude
- `end_lat` (required): Destination latitude
- `end_lng` (required): Destination longitude
- `mode` (optional): Transportation mode (`walking`, `driving`, `cycling`)

**Response:**
```json
{
  "distance": 1250.5,
  "duration": 900.2,
  "steps": [
    {
      "step": 1,
      "instruction": "Start by heading north on Main St",
      "distance": 150.0,
      "duration": 120.0,
      "direction": "↑",
      "coordinates": [-122.3321, 47.6062]
    },
    {
      "step": 2,
      "instruction": "Turn right onto 1st Ave",
      "distance": 200.0,
      "duration": 150.0,
      "direction": "→",
      "coordinates": [-122.3300, 47.6070]
    }
  ],
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [-122.3321, 47.6062],
      [-122.3300, 47.6070],
      [-122.3493, 47.6205]
    ]
  }
}
```

### 3. Get Full Directions

**Endpoint:** `POST /api/directions`

**Description:** Get complete directions from human-readable addresses.

**Request Body:**
```json
{
  "start_address": "123 Main St, Seattle, WA",
  "end_address": "456 Pine St, Seattle, WA",
  "mode": "walking"
}
```

**Parameters:**
- `start_address` (required): Starting address
- `end_address` (required): Destination address
- `mode` (optional): Transportation mode (`walking`, `driving`, `cycling`)

**Response:**
```json
{
  "start": {
    "lat": 47.6062,
    "lng": -122.3321,
    "display_name": "123 Main St, Seattle, WA 98101, USA",
    "address": {
      "house_number": "123",
      "road": "Main St",
      "city": "Seattle",
      "state": "Washington"
    }
  },
  "end": {
    "lat": 47.6205,
    "lng": -122.3493,
    "display_name": "456 Pine St, Seattle, WA 98101, USA",
    "address": {
      "house_number": "456",
      "road": "Pine St",
      "city": "Seattle",
      "state": "Washington"
    }
  },
  "route": {
    "distance": 1250.5,
    "duration": 900.2,
    "steps": [
      {
        "step": 1,
        "instruction": "Start by heading north on Main St",
        "distance": 150.0,
        "duration": 120.0,
        "direction": "↑",
        "coordinates": [-122.3321, 47.6062]
      }
    ],
    "geometry": {
      "type": "LineString",
      "coordinates": [
        [-122.3321, 47.6062],
        [-122.3493, 47.6205]
      ]
    }
  }
}
```

### 4. Health Check

**Endpoint:** `GET /api/health`

**Description:** Check API status and external service dependencies.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "services": {
    "nominatim": "https://nominatim.openstreetmap.org",
    "osrm": "https://router.project-osrm.org"
  }
}
```

## Error Handling

### Standard Error Response

```json
{
  "error": "Error message describing what went wrong"
}
```

### Common Error Messages

- `"Address is required"`: Missing address parameter
- `"All coordinates are required"`: Missing coordinate parameters
- `"Both start and end addresses are required"`: Missing address parameters
- `"Address not found: [address]"`: Geocoding failed for the given address
- `"No route found"`: No route could be calculated between the points
- `"Routing failed: [message]"`: General routing error
- `"Server error: [message]"`: Internal server error

## Transportation Modes

### Walking (`walking`)
- Uses GraphHopper for pedestrian-optimized routing
- Includes sidewalks, crosswalks, and accessibility features
- Fallback to OSRM if GraphHopper is unavailable

### Driving (`driving`)
- Uses OSRM with car routing profile
- Includes highways and major roads
- Optimized for vehicle navigation

### Cycling (`cycling`)
- Uses OSRM with bicycle routing profile
- Includes bike lanes and bike-friendly paths
- Avoids highways and major roads

## Rate Limits

- No rate limits currently implemented
- Respectful usage of external services (Nominatim, OSRM, GraphHopper)
- User-Agent header required for service identification

## CORS Support

- Cross-Origin Resource Sharing (CORS) enabled
- Allows frontend applications to make requests
- No authentication headers required

## External Dependencies

### Nominatim (Geocoding)
- **URL:** `https://nominatim.openstreetmap.org`
- **Purpose:** Address to coordinates conversion
- **Rate Limit:** 1 request per second (respectful usage)

### OSRM (Routing)
- **URL:** `https://router.project-osrm.org`
- **Purpose:** Route calculation for driving and cycling
- **Rate Limit:** No official limit (respectful usage)

### GraphHopper (Pedestrian Routing)
- **URL:** `https://graphhopper.com/api/1`
- **Purpose:** Walking route optimization
- **Rate Limit:** Free tier with demo key

## Accessibility Features

### Voice Guidance
- Turn-by-turn voice announcements
- Distance and direction information
- Error message announcements
- Status updates and confirmations

### Visual Accessibility
- Unicode direction arrows for screen readers
- High contrast color schemes
- Clear typography and spacing
- Keyboard navigation support

### Speech Recognition
- Voice input for addresses
- Real-time transcription feedback
- Error handling and retry mechanisms
- Cross-browser compatibility

## Development Notes

### Debug Information
- Console logging for development
- API response debugging
- Error tracking and reporting
- Performance monitoring

### Testing
- Health check endpoint for monitoring
- Error simulation and handling
- Cross-browser compatibility testing
- Accessibility testing with screen readers

## Future Enhancements

### Planned Features
- Real-time traffic information
- Alternative route suggestions
- Offline map support
- Enhanced accessibility features
- Multi-language support
- Custom voice settings
- Route sharing and saving
- Integration with assistive technologies
