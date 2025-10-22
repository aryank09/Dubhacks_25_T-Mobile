"""
Text Maps Backend - Accessible Navigation API

This Flask application provides a REST API for accessible navigation services,
including geocoding, routing, and turn-by-turn directions with voice guidance support.
The API integrates with OpenStreetMap services (Nominatim, OSRM, GraphHopper) to provide
comprehensive navigation data optimized for accessibility.

Key Features:
- Address geocoding using OpenStreetMap Nominatim
- Multi-modal routing (walking, driving, cycling)
- Turn-by-turn directions with accessibility considerations
- Voice guidance support for visually impaired users
- Real-time location tracking for live navigation

API Endpoints:
- POST /api/geocode - Convert addresses to coordinates
- POST /api/route - Get route between coordinates
- POST /api/directions - Get full directions from addresses
- GET /api/health - Health check endpoint
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time
from datetime import datetime

# Initialize Flask application with CORS support for frontend integration
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend-backend communication

# External service configuration
# These URLs point to free, open-source mapping services
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"  # Geocoding service
OSRM_BASE_URL = "https://router.project-osrm.org"           # Routing service
GRAPHHOPPER_BASE_URL = "https://graphhopper.com/api/1"      # Alternative routing service

def geocode_address(address):
    """
    Convert a human-readable address to geographic coordinates using OpenStreetMap Nominatim.
    
    This function handles address geocoding with special support for current location
    requests and provides detailed address information for accessibility features.
    
    Args:
        address (str): The address to geocode. Can be:
            - A full address (e.g., "123 Main St, Seattle, WA")
            - A landmark name (e.g., "Space Needle, Seattle")
            - Special keywords: "current", "current location", "my location", "here"
    
    Returns:
        dict: Geocoding result containing:
            - lat (float): Latitude coordinate
            - lng (float): Longitude coordinate  
            - display_name (str): Full formatted address
            - address (dict): Structured address components
    
    Raises:
        ValueError: If address cannot be found or geocoding fails
        
    Note:
        Returns None for current location requests - these are handled by frontend GPS
    """
    try:
        # Handle special current location requests
        if address.lower() in ['current', 'current location', 'my location', 'here']:
            return None  # Will be handled by frontend GPS using browser geolocation
        
        # Prepare Nominatim API request parameters
        params = {
            'q': address,                    # Query string (the address to search)
            'format': 'json',               # Response format
            'limit': 1,                     # Maximum number of results
            'addressdetails': 1             # Include detailed address components
        }
        
        # Set user agent as required by Nominatim usage policy
        headers = {
            'User-Agent': 'TextMaps/1.0 (Navigation App; https://github.com/your-repo/text-maps)'
        }
        
        # Make request to Nominatim geocoding service
        response = requests.get(f"{NOMINATIM_BASE_URL}/search", params=params, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        if not data:
            raise ValueError(f"Address not found: {address}")
        
        # Extract first (most relevant) result
        result = data[0]
        return {
            'lat': float(result['lat']),           # Latitude as float
            'lng': float(result['lon']),           # Longitude as float
            'display_name': result['display_name'], # Human-readable address
            'address': result.get('address', {})   # Structured address components
        }
    except Exception as e:
        raise ValueError(f"Geocoding failed: {str(e)}")

def get_route_graphhopper(start_lat, start_lng, end_lat, end_lng):
    """
    Get walking route using GraphHopper routing service with enhanced pedestrian support.
    
    GraphHopper provides superior pedestrian routing compared to OSRM, with better
    support for sidewalks, crosswalks, and accessibility features. This function
    is specifically optimized for walking routes and includes fallback to OSRM.
    
    Args:
        start_lat (float): Starting latitude coordinate
        start_lng (float): Starting longitude coordinate
        end_lat (float): Destination latitude coordinate
        end_lng (float): Destination longitude coordinate
    
    Returns:
        dict: Route data containing:
            - distance (float): Total route distance in meters
            - duration (float): Estimated travel time in seconds
            - steps (list): Turn-by-turn directions with accessibility info
            - geometry (dict): GeoJSON LineString of the route path
    
    Raises:
        ValueError: If no route can be found or service fails
        
    Note:
        Falls back to OSRM if GraphHopper service is unavailable
    """
    try:
        # GraphHopper free tier configuration (no API key required for basic usage)
        url = f"{GRAPHHOPPER_BASE_URL}/route"
        params = {
            'point': [f"{start_lat},{start_lng}", f"{end_lat},{end_lng}"],  # Start and end points
            'vehicle': 'foot',                    # Pedestrian routing mode
            'instructions': 'true',              # Include turn-by-turn instructions
            'points_encoded': 'false',           # Return coordinates as lat/lng pairs
            'key': 'demo'                        # Free demo API key
        }
        
        headers = {
            'User-Agent': 'TextMaps/1.0 (Navigation App; https://github.com/your-repo/text-maps)'
        }
        
        print(f"DEBUG: Using GraphHopper for walking route")
        print(f"DEBUG: URL: {url}")
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if 'paths' not in data or not data['paths']:
            raise ValueError("No route found")
        
        path = data['paths'][0]
        
        # Convert GraphHopper response to standardized format
        steps = []
        for i, instruction in enumerate(path.get('instructions', [])):
            step_num = i + 1
            instruction_text = instruction.get('text', 'Continue')
            distance = instruction.get('distance', 0)
            time = instruction.get('time', 0)
            
            # Get direction arrow for visual accessibility
            bearing = instruction.get('bearing_after', 0)
            direction = get_direction_arrow(bearing)
            
            # Format instruction with accessibility considerations
            if i == 0:
                instruction_text = f"Start by heading {get_direction_name(bearing)} on {instruction_text}"
            elif i == len(path.get('instructions', [])) - 1:
                instruction_text = f"Arrive at your destination"
            
            steps.append({
                'step': step_num,
                'instruction': instruction_text,
                'distance': distance,
                'duration': time / 1000,  # Convert from milliseconds to seconds
                'direction': direction,
                'coordinates': [instruction.get('location', [])[1], instruction.get('location', [])[0]]
            })
        
        return {
            'distance': path.get('distance', 0),
            'duration': path.get('time', 0) / 1000,  # Convert from milliseconds to seconds
            'steps': steps,
            'geometry': {
                'type': 'LineString',
                'coordinates': path.get('points', {}).get('coordinates', [])
            }
        }
        
    except Exception as e:
        print(f"DEBUG: GraphHopper failed: {str(e)}")
        # Fallback to OSRM if GraphHopper fails
        return get_route_osrm_fallback(start_lat, start_lng, end_lat, end_lng)

def get_route_osrm_fallback(start_lat, start_lng, end_lat, end_lng):
    """
    Fallback OSRM routing service for walking routes when GraphHopper is unavailable.
    
    This function provides a backup routing solution using the Open Source Routing Machine (OSRM)
    service. While not as optimized for pedestrians as GraphHopper, it provides reliable
    turn-by-turn directions with detailed maneuver information.
    
    Args:
        start_lat (float): Starting latitude coordinate
        start_lng (float): Starting longitude coordinate
        end_lat (float): Destination latitude coordinate
        end_lng (float): Destination longitude coordinate
    
    Returns:
        dict: Route data containing:
            - distance (float): Total route distance in meters
            - duration (float): Estimated travel time in seconds
            - steps (list): Turn-by-turn directions with maneuver details
            - geometry (dict): GeoJSON LineString of the route path
    
    Raises:
        ValueError: If routing fails or no route can be found
    """
    try:
        # OSRM API endpoint for foot (walking) routing
        url = f"{OSRM_BASE_URL}/route/v1/foot/{start_lng},{start_lat};{end_lng},{end_lat}"
        params = {
            'overview': 'full',        # Full route geometry
            'steps': 'true',          # Include turn-by-turn steps
            'geometries': 'geojson',   # Return geometry as GeoJSON
            'annotations': 'true'     # Include additional route metadata
        }
        
        headers = {
            'User-Agent': 'TextMaps/1.0 (Navigation App; https://github.com/your-repo/text-maps)'
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data['code'] != 'Ok':
            raise ValueError(f"Routing failed: {data.get('message', 'Unknown error')}")
        
        route = data['routes'][0]
        legs = data['routes'][0]['legs'][0]
        
        # Process steps into turn-by-turn directions with accessibility features
        steps = []
        for i, step in enumerate(legs['steps']):
            maneuver = step['maneuver']
            instruction = step.get('name', 'Continue')
            distance = step['distance']
            duration = step['duration']
            
            # Get direction arrow for visual accessibility
            bearing_after = maneuver.get('bearing_after', 0)
            direction = get_direction_arrow(bearing_after)
            
            # Format instruction with accessibility considerations
            if i == 0:
                instruction_text = f"Start by heading {get_direction_name(bearing_after)} on {instruction}"
            elif i == len(legs['steps']) - 1:
                instruction_text = f"Arrive at your destination"
            else:
                maneuver_type = maneuver.get('type', 'turn')
                if maneuver_type == 'turn':
                    turn_type = maneuver.get('modifier', 'straight')
                    instruction_text = f"{direction} Turn {turn_type} onto {instruction}"
                else:
                    instruction_text = f"{direction} {instruction}"
            
            steps.append({
                'step': i + 1,
                'instruction': instruction_text,
                'distance': distance,
                'duration': duration,
                'direction': direction,
                'coordinates': maneuver['location']
            })
        
        return {
            'distance': route['distance'],
            'duration': route['duration'],
            'steps': steps,
            'geometry': route['geometry']
        }
        
    except Exception as e:
        raise ValueError(f"Routing failed: {str(e)}")

def get_route(start_lat, start_lng, end_lat, end_lng, mode='walking'):
    """
    Get route between two points using the most appropriate routing service.
    
    This is the main routing function that intelligently selects between GraphHopper
    (for walking) and OSRM (for driving/cycling) based on the transportation mode.
    It provides comprehensive turn-by-turn directions optimized for accessibility.
    
    Args:
        start_lat (float): Starting latitude coordinate
        start_lng (float): Starting longitude coordinate
        end_lat (float): Destination latitude coordinate
        end_lng (float): Destination longitude coordinate
        mode (str): Transportation mode - 'walking', 'driving', or 'cycling'
    
    Returns:
        dict: Complete route data containing:
            - distance (float): Total route distance in meters
            - duration (float): Estimated travel time in seconds
            - steps (list): Turn-by-turn directions with accessibility features
            - geometry (dict): GeoJSON LineString of the route path
    
    Raises:
        ValueError: If routing fails or no route can be found
        
    Note:
        - Walking routes use GraphHopper for better pedestrian support
        - Driving and cycling routes use OSRM for comprehensive road network coverage
    """
    try:
        # For walking routes, use GraphHopper which has better pedestrian support
        if mode == 'walking':
            return get_route_graphhopper(start_lat, start_lng, end_lat, end_lng)
        
        # For driving and cycling, use OSRM for comprehensive road network coverage
        profile_map = {
            'driving': 'driving',    # Car routing with highway access
            'cycling': 'cycling'     # Bicycle routing with bike-friendly paths
        }
        
        profile = profile_map.get(mode, 'driving')
        
        # OSRM route request with comprehensive parameters
        url = f"{OSRM_BASE_URL}/route/v1/{profile}/{start_lng},{start_lat};{end_lng},{end_lat}"
        params = {
            'overview': 'full',        # Full route geometry for mapping
            'steps': 'true',          # Include turn-by-turn steps
            'geometries': 'geojson',   # Return geometry as GeoJSON
            'annotations': 'true'     # Include additional route metadata
        }
        
        headers = {
            'User-Agent': 'TextMaps/1.0 (Navigation App; https://github.com/your-repo/text-maps)'
        }
        
        print(f"DEBUG: Requesting route with profile: {profile}, mode: {mode}")
        print(f"DEBUG: URL: {url}")
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"DEBUG: Response code: {data.get('code', 'No code')}")
        print(f"DEBUG: Number of routes: {len(data.get('routes', []))}")
        
        if data['code'] != 'Ok':
            raise ValueError(f"Routing failed: {data.get('message', 'Unknown error')}")
        
        route = data['routes'][0]
        legs = data['routes'][0]['legs'][0]
        
        print(f"DEBUG: Route distance: {route.get('distance', 'No distance')}m")
        print(f"DEBUG: Route duration: {route.get('duration', 'No duration')}s")
        print(f"DEBUG: Number of steps: {len(legs.get('steps', []))}")
        
        # Process steps into turn-by-turn directions with accessibility features
        steps = []
        for i, step in enumerate(legs['steps']):
            maneuver = step['maneuver']
            instruction = step.get('name', 'Continue')
            distance = step['distance']
            duration = step['duration']
            
            # Get direction arrow for visual accessibility
            bearing_after = maneuver.get('bearing_after', 0)
            direction = get_direction_arrow(bearing_after)
            
            # Format instruction with accessibility considerations
            if i == 0:
                instruction_text = f"Start by heading {get_direction_name(bearing_after)} on {instruction}"
            elif i == len(legs['steps']) - 1:
                instruction_text = f"Arrive at your destination"
            else:
                maneuver_type = maneuver.get('type', 'turn')
                if maneuver_type == 'turn':
                    turn_type = maneuver.get('modifier', 'straight')
                    instruction_text = f"{direction} Turn {turn_type} onto {instruction}"
                else:
                    instruction_text = f"{direction} {instruction}"
            
            steps.append({
                'step': i + 1,
                'instruction': instruction_text,
                'distance': distance,
                'duration': duration,
                'direction': direction,
                'coordinates': maneuver['location']
            })
        
        return {
            'distance': route['distance'],
            'duration': route['duration'],
            'steps': steps,
            'geometry': route['geometry']
        }
        
    except Exception as e:
        raise ValueError(f"Routing failed: {str(e)}")

def get_direction_arrow(bearing):
    """
    Convert compass bearing to Unicode direction arrow for visual accessibility.
    
    This function provides visual direction indicators that are essential for
    accessibility, helping users with visual impairments understand turn directions
    through screen readers and other assistive technologies.
    
    Args:
        bearing (float): Compass bearing in degrees (0-360)
    
    Returns:
        str: Unicode arrow character representing the direction
            - ↑ (north), ↗ (northeast), → (east), ↘ (southeast)
            - ↓ (south), ↙ (southwest), ← (west), ↖ (northwest)
    """
    if bearing is None:
        return "→"  # Default to right arrow for unknown directions
    
    # Convert bearing to direction using 8-point compass system
    directions = {
        (0, 22.5): "↑",        # North
        (22.5, 67.5): "↗",     # Northeast
        (67.5, 112.5): "→",    # East
        (112.5, 157.5): "↘",   # Southeast
        (157.5, 202.5): "↓",   # South
        (202.5, 247.5): "↙",   # Southwest
        (247.5, 292.5): "←",  # West
        (292.5, 337.5): "↖",  # Northwest
        (337.5, 360): "↑"      # North (wrap-around)
    }
    
    for (start, end), arrow in directions.items():
        if start <= bearing < end:
            return arrow
    return "→"  # Default fallback

def get_direction_name(bearing):
    """
    Convert compass bearing to human-readable direction name for voice guidance.
    
    This function provides spoken direction names that are essential for
    accessibility, enabling voice guidance systems to announce directions
    in a natural, understandable format for users with visual impairments.
    
    Args:
        bearing (float): Compass bearing in degrees (0-360)
    
    Returns:
        str: Human-readable direction name
            - "north", "northeast", "east", "southeast"
            - "south", "southwest", "west", "northwest"
    """
    if bearing is None:
        return "straight"  # Default for unknown directions
    
    # Convert bearing to direction using 8-point compass system
    directions = {
        (0, 22.5): "north",        # North
        (22.5, 67.5): "northeast", # Northeast
        (67.5, 112.5): "east",     # East
        (112.5, 157.5): "southeast", # Southeast
        (157.5, 202.5): "south",   # South
        (202.5, 247.5): "southwest", # Southwest
        (247.5, 292.5): "west",    # West
        (292.5, 337.5): "northwest", # Northwest
        (337.5, 360): "north"      # North (wrap-around)
    }
    
    for (start, end), direction in directions.items():
        if start <= bearing < end:
            return direction
    return "straight"  # Default fallback

@app.route('/api/geocode', methods=['POST'])
def geocode():
    """
    API endpoint to convert human-readable addresses to geographic coordinates.
    
    This endpoint handles address geocoding with special support for current location
    requests and provides detailed address information for accessibility features.
    
    Request Body:
        address (str): The address to geocode
    
    Returns:
        JSON: Geocoding result containing:
            - lat (float): Latitude coordinate
            - lng (float): Longitude coordinate
            - display_name (str): Full formatted address
            - address (dict): Structured address components
    
    Status Codes:
        200: Success
        400: Bad request (missing address or geocoding failed)
        500: Server error
    """
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        result = geocode_address(address)
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/route', methods=['POST'])
def route():
    """
    API endpoint to get route between two geographic coordinates.
    
    This endpoint provides turn-by-turn directions between two points using the
    most appropriate routing service based on the transportation mode.
    
    Request Body:
        start_lat (float): Starting latitude coordinate
        start_lng (float): Starting longitude coordinate
        end_lat (float): Destination latitude coordinate
        end_lng (float): Destination longitude coordinate
        mode (str, optional): Transportation mode - 'walking', 'driving', or 'cycling' (default: 'walking')
    
    Returns:
        JSON: Route data containing:
            - distance (float): Total route distance in meters
            - duration (float): Estimated travel time in seconds
            - steps (list): Turn-by-turn directions with accessibility features
            - geometry (dict): GeoJSON LineString of the route path
    
    Status Codes:
        200: Success
        400: Bad request (missing coordinates or routing failed)
        500: Server error
    """
    try:
        data = request.get_json()
        
        start_lat = data.get('start_lat')
        start_lng = data.get('start_lng')
        end_lat = data.get('end_lat')
        end_lng = data.get('end_lng')
        mode = data.get('mode', 'walking')
        
        if not all([start_lat, start_lng, end_lat, end_lng]):
            return jsonify({'error': 'All coordinates are required'}), 400
        
        result = get_route(start_lat, start_lng, end_lat, end_lng, mode)
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/directions', methods=['POST'])
def directions():
    """
    API endpoint to get complete directions from human-readable addresses.
    
    This is the main endpoint for the navigation system, combining geocoding
    and routing to provide complete turn-by-turn directions from addresses.
    
    Request Body:
        start_address (str): Starting address or location
        end_address (str): Destination address or location
        mode (str, optional): Transportation mode - 'walking', 'driving', or 'cycling' (default: 'walking')
    
    Returns:
        JSON: Complete directions containing:
            - start (dict): Starting location with coordinates and address
            - end (dict): Destination location with coordinates and address
            - route (dict): Route data with turn-by-turn directions
    
    Status Codes:
        200: Success
        400: Bad request (missing addresses or processing failed)
        500: Server error
    """
    try:
        data = request.get_json()
        
        start_address = data.get('start_address')
        end_address = data.get('end_address')
        mode = data.get('mode', 'walking')
        
        if not start_address or not end_address:
            return jsonify({'error': 'Both start and end addresses are required'}), 400
        
        # Geocode both addresses to get coordinates
        start_coords = geocode_address(start_address)
        end_coords = geocode_address(end_address)
        
        # Get route between the geocoded coordinates
        route_data = get_route(
            start_coords['lat'], start_coords['lng'],
            end_coords['lat'], end_coords['lng'],
            mode
        )
        
        return jsonify({
            'start': start_coords,
            'end': end_coords,
            'route': route_data
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint for monitoring service status.
    
    This endpoint provides information about the API status and external
    service dependencies for monitoring and debugging purposes.
    
    Returns:
        JSON: Health status containing:
            - status (str): Service status ('healthy')
            - timestamp (str): Current timestamp in ISO format
            - services (dict): External service URLs and status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'nominatim': 'https://nominatim.openstreetmap.org',
            'osrm': 'https://router.project-osrm.org'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
