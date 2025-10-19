from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
OSRM_BASE_URL = "https://router.project-osrm.org"
GRAPHHOPPER_BASE_URL = "https://graphhopper.com/api/1"

def geocode_address(address):
    """Convert address to coordinates using OpenStreetMap Nominatim"""
    try:
        if address.lower() in ['current', 'current location', 'my location', 'here']:
            return None  # Will be handled by frontend GPS
        
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'TextMaps/1.0 (Navigation App; https://github.com/your-repo/text-maps)'
        }
        
        response = requests.get(f"{NOMINATIM_BASE_URL}/search", params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            raise ValueError(f"Address not found: {address}")
        
        result = data[0]
        return {
            'lat': float(result['lat']),
            'lng': float(result['lon']),
            'display_name': result['display_name'],
            'address': result.get('address', {})
        }
    except Exception as e:
        raise ValueError(f"Geocoding failed: {str(e)}")

def get_route_graphhopper(start_lat, start_lng, end_lat, end_lng):
    """Get walking route using GraphHopper (better pedestrian support)"""
    try:
        # GraphHopper free tier (no API key required for basic usage)
        url = f"{GRAPHHOPPER_BASE_URL}/route"
        params = {
            'point': [f"{start_lat},{start_lng}", f"{end_lat},{end_lng}"],
            'vehicle': 'foot',
            'instructions': 'true',
            'points_encoded': 'false',
            'key': 'demo'  # Free demo key
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
        
        # Convert GraphHopper response to our format
        steps = []
        for i, instruction in enumerate(path.get('instructions', [])):
            step_num = i + 1
            instruction_text = instruction.get('text', 'Continue')
            distance = instruction.get('distance', 0)
            time = instruction.get('time', 0)
            
            # Get direction arrow
            bearing = instruction.get('bearing_after', 0)
            direction = get_direction_arrow(bearing)
            
            # Format instruction
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
    """Fallback OSRM route for walking"""
    try:
        url = f"{OSRM_BASE_URL}/route/v1/foot/{start_lng},{start_lat};{end_lng},{end_lat}"
        params = {
            'overview': 'full',
            'steps': 'true',
            'geometries': 'geojson',
            'annotations': 'true'
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
        
        # Process steps into turn-by-turn directions
        steps = []
        for i, step in enumerate(legs['steps']):
            maneuver = step['maneuver']
            instruction = step.get('name', 'Continue')
            distance = step['distance']
            duration = step['duration']
            
            # Get direction arrow
            bearing_after = maneuver.get('bearing_after', 0)
            direction = get_direction_arrow(bearing_after)
            
            # Format instruction
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
    """Get route between two points using OSRM or GraphHopper"""
    try:
        # For walking routes, use GraphHopper which has better pedestrian support
        if mode == 'walking':
            return get_route_graphhopper(start_lat, start_lng, end_lat, end_lng)
        
        # For driving and cycling, use OSRM
        profile_map = {
            'driving': 'driving',
            'cycling': 'cycling'
        }
        
        profile = profile_map.get(mode, 'driving')
        
        # OSRM route request
        url = f"{OSRM_BASE_URL}/route/v1/{profile}/{start_lng},{start_lat};{end_lng},{end_lat}"
        params = {
            'overview': 'full',
            'steps': 'true',
            'geometries': 'geojson',
            'annotations': 'true'
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
        
        # Process steps into turn-by-turn directions
        steps = []
        for i, step in enumerate(legs['steps']):
            maneuver = step['maneuver']
            instruction = step.get('name', 'Continue')
            distance = step['distance']
            duration = step['duration']
            
            # Get direction arrow
            bearing_after = maneuver.get('bearing_after', 0)
            direction = get_direction_arrow(bearing_after)
            
            # Format instruction
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
    """Convert bearing to direction arrow"""
    if bearing is None:
        return "→"
    
    # Convert bearing to direction
    directions = {
        (0, 22.5): "↑", (22.5, 67.5): "↗", (67.5, 112.5): "→",
        (112.5, 157.5): "↘", (157.5, 202.5): "↓", (202.5, 247.5): "↙",
        (247.5, 292.5): "←", (292.5, 337.5): "↖", (337.5, 360): "↑"
    }
    
    for (start, end), arrow in directions.items():
        if start <= bearing < end:
            return arrow
    return "→"

def get_direction_name(bearing):
    """Convert bearing to direction name"""
    if bearing is None:
        return "straight"
    
    directions = {
        (0, 22.5): "north", (22.5, 67.5): "northeast", (67.5, 112.5): "east",
        (112.5, 157.5): "southeast", (157.5, 202.5): "south", (202.5, 247.5): "southwest",
        (247.5, 292.5): "west", (292.5, 337.5): "northwest", (337.5, 360): "north"
    }
    
    for (start, end), direction in directions.items():
        if start <= bearing < end:
            return direction
    return "straight"

@app.route('/api/geocode', methods=['POST'])
def geocode():
    """Geocode an address to coordinates"""
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
    """Get route between two points"""
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
    """Get full directions from addresses"""
    try:
        data = request.get_json()
        
        start_address = data.get('start_address')
        end_address = data.get('end_address')
        mode = data.get('mode', 'walking')
        
        if not start_address or not end_address:
            return jsonify({'error': 'Both start and end addresses are required'}), 400
        
        # Geocode both addresses
        start_coords = geocode_address(start_address)
        end_coords = geocode_address(end_address)
        
        # Get route
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
    """Health check endpoint"""
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
