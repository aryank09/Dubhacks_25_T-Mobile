#!/usr/bin/env python3
"""
Text-based Navigation System
A Google Maps alternative that provides turn-by-turn directions via text
"""

import requests
import sys
from typing import Dict, List, Tuple, Optional
import json
import geocoder
import time
import math
import platform


class TextMaps:
    """Text-based navigation system using OpenStreetMap and OSRM"""
    
    def __init__(self, mode='walking'):
        """
        Initialize TextMaps
        
        Args:
            mode: Transportation mode - 'walking', 'driving', 'cycling'
        """
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.mode = mode
        self.osrm_url = f"http://router.project-osrm.org/route/v1/{mode}"
        self.headers = {
            'User-Agent': 'TextMaps/1.0'
        }
    
    def get_current_location_from_browser(self) -> Optional[Tuple[float, float]]:
        """
        Get precise GPS location using browser-based geolocation API
        Opens a simple web server to get HTML5 geolocation
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading
            import urllib.parse
            
            location_data = {'lat': None, 'lon': None, 'received': False}
            
            class LocationHandler(BaseHTTPRequestHandler):
                def log_message(self, format, *args):
                    pass  # Suppress logging
                
                def do_GET(self):
                    if self.path == '/':
                        # Serve HTML page with geolocation
                        html = '''
                        <!DOCTYPE html>
                        <html>
                        <head><title>GPS Location</title></head>
                        <body>
                        <h2>📍 Getting your GPS location...</h2>
                        <p id="status">Requesting location permission...</p>
                        <script>
                        if (navigator.geolocation) {
                            navigator.geolocation.getCurrentPosition(
                                function(position) {
                                    document.getElementById('status').textContent = 'Location acquired! You can close this window.';
                                    fetch('/location?lat=' + position.coords.latitude + '&lon=' + position.coords.longitude);
                                },
                                function(error) {
                                    document.getElementById('status').textContent = 'Error: ' + error.message;
                                },
                                {enableHighAccuracy: true, timeout: 10000}
                            );
                        } else {
                            document.getElementById('status').textContent = 'Geolocation not supported';
                        }
                        </script>
                        </body>
                        </html>
                        '''
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(html.encode())
                    elif self.path.startswith('/location'):
                        # Parse location data
                        query = urllib.parse.urlparse(self.path).query
                        params = urllib.parse.parse_qs(query)
                        if 'lat' in params and 'lon' in params:
                            location_data['lat'] = float(params['lat'][0])
                            location_data['lon'] = float(params['lon'][0])
                            location_data['received'] = True
                        self.send_response(200)
                        self.end_headers()
            
            # Start server in background
            server = HTTPServer(('localhost', 8888), LocationHandler)
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            
            # Open browser
            import webbrowser
            print("🌐 Opening browser to get your precise GPS location...")
            print("   Please allow location access when prompted.")
            webbrowser.open('http://localhost:8888')
            
            # Wait for location (max 30 seconds)
            for _ in range(60):
                if location_data['received']:
                    server.shutdown()
                    return (location_data['lat'], location_data['lon'])
                time.sleep(0.5)
            
            server.shutdown()
            return None
            
        except Exception as e:
            print(f"⚠️  Error getting browser location: {e}")
            return None
    
    def get_current_location(self, use_gps: bool = True) -> Optional[Tuple[float, float]]:
        """
        Get current location using GPS or IP-based geolocation
        
        Args:
            use_gps: If True, try to use device GPS first
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            if use_gps:
                # Try browser-based GPS (most accurate)
                location = self.get_current_location_from_browser()
                if location:
                    return location
            
            # Fallback to IP-based geolocation
            print("📍 Using IP-based location (less accurate)...")
            g = geocoder.ip('me')
            if g.ok and g.latlng:
                return (g.latlng[0], g.latlng[1])
            
            return None
        except Exception as e:
            print(f"⚠️  Error getting current location: {e}")
            return None
    
    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates (latitude, longitude)
        
        Args:
            address: Street address or place name
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        
        try:
            response = requests.get(
                self.nominatim_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            results = response.json()
            
            if results:
                lat = float(results[0]['lat'])
                lon = float(results[0]['lon'])
                return (lat, lon)
            else:
                return None
                
        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None
    
    def get_route(self, start_coords: Tuple[float, float], 
                  end_coords: Tuple[float, float]) -> Optional[Dict]:
        """
        Get route between two coordinates
        
        Args:
            start_coords: (latitude, longitude) of starting point
            end_coords: (latitude, longitude) of destination
            
        Returns:
            Route data dictionary or None if route not found
        """
        # OSRM uses lon,lat format (opposite of typical lat,lon)
        start_lon, start_lat = start_coords[1], start_coords[0]
        end_lon, end_lat = end_coords[1], end_coords[0]
        
        url = f"{self.osrm_url}/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            'overview': 'full',
            'steps': 'true',
            'geometries': 'geojson'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 'Ok':
                return data
            else:
                return None
                
        except Exception as e:
            print(f"Error getting route: {e}")
            return None
    
    def format_distance(self, meters: float) -> str:
        """Format distance in human-readable form"""
        if meters < 1000:
            return f"{int(meters)} meters"
        else:
            km = meters / 1000
            return f"{km:.1f} km"
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form"""
        minutes = int(seconds / 60)
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} {mins} min"
        else:
            return f"{mins} minute{'s' if mins != 1 else ''}"
    
    def get_direction_icon(self, modifier: str, direction_type: str) -> str:
        """Get a text icon for the direction"""
        icons = {
            'turn': {
                'left': '←',
                'right': '→',
                'sharp left': '↰',
                'sharp right': '↱',
                'slight left': '↖',
                'slight right': '↗',
                'straight': '↑',
                'uturn': '↶'
            },
            'depart': '🚶' if self.mode == 'walking' else '🚗',
            'arrive': '🎯' if self.mode == 'walking' else '🏁',
            'merge': '⤴',
            'roundabout': '⟲',
            'fork': '⑂'
        }
        
        if direction_type in ['depart', 'arrive', 'merge', 'roundabout', 'fork']:
            return icons.get(direction_type, '→')
        
        return icons.get('turn', {}).get(modifier, '→')
    
    def format_instruction(self, step: Dict, step_num: int) -> str:
        """Format a single navigation instruction"""
        maneuver = step['maneuver']
        distance = step['distance']
        direction_type = maneuver['type']
        modifier = maneuver.get('modifier', '')
        
        # Get the instruction text
        instruction = step.get('name', 'the road')
        
        # Get direction icon
        icon = self.get_direction_icon(modifier, direction_type)
        
        # Format the step with walking-friendly language
        action_verb = "Walk" if self.mode == 'walking' else "Head"
        
        if direction_type == 'depart':
            text = f"{action_verb} {modifier} on {instruction}"
        elif direction_type == 'arrive':
            text = f"Arrive at your destination"
        elif direction_type == 'turn':
            text = f"Turn {modifier} onto {instruction}"
        elif direction_type == 'merge':
            text = f"Merge {modifier} onto {instruction}"
        elif direction_type == 'roundabout':
            exit_num = maneuver.get('exit', 1)
            text = f"At roundabout, take exit {exit_num} onto {instruction}"
        elif direction_type == 'fork':
            text = f"At fork, keep {modifier} onto {instruction}"
        else:
            text = f"{direction_type.replace('_', ' ').title()} {modifier} onto {instruction}"
        
        # Add distance
        dist_text = self.format_distance(distance)
        
        return f"{step_num}. {icon} {text} ({dist_text})"
    
    def print_directions(self, start_address: str, end_address: str):
        """
        Get and print turn-by-turn directions
        
        Args:
            start_address: Starting location (or "current" for current location)
            end_address: Destination (or "current" for current location)
        """
        print(f"\n{'='*60}")
        print(f"Getting directions from:")
        print(f"  📍 {start_address}")
        print(f"to:")
        print(f"  📍 {end_address}")
        print(f"{'='*60}\n")
        
        # Geocode addresses
        print("🔍 Finding locations...")
        
        # Handle current location for start
        if start_address.lower() in ['current', 'current location', 'my location', 'here']:
            print("📍 Detecting your current location...")
            start_coords = self.get_current_location()
            if not start_coords:
                print(f"❌ Could not detect current location. Please enter an address instead.")
                return
            print(f"✓ Current location detected!")
        else:
            start_coords = self.geocode(start_address)
            if not start_coords:
                print(f"❌ Could not find starting location: {start_address}")
                return
        
        # Handle current location for destination
        if end_address.lower() in ['current', 'current location', 'my location', 'here']:
            print("📍 Detecting your current location...")
            end_coords = self.get_current_location()
            if not end_coords:
                print(f"❌ Could not detect current location. Please enter an address instead.")
                return
            print(f"✓ Current location detected!")
        else:
            end_coords = self.geocode(end_address)
            if not end_coords:
                print(f"❌ Could not find destination: {end_address}")
                return
        
        print(f"✓ Start: {start_coords[0]:.4f}, {start_coords[1]:.4f}")
        print(f"✓ End: {end_coords[0]:.4f}, {end_coords[1]:.4f}\n")
        
        # Get route
        print("🗺️  Calculating route...\n")
        route_data = self.get_route(start_coords, end_coords)
        
        if not route_data or not route_data.get('routes'):
            print("❌ Could not find a route between these locations")
            return
        
        route = route_data['routes'][0]
        total_distance = route['distance']
        total_duration = route['duration']
        
        # Print summary
        print(f"{'='*60}")
        print(f"📊 ROUTE SUMMARY")
        print(f"{'='*60}")
        print(f"Total Distance: {self.format_distance(total_distance)}")
        print(f"Estimated Time: {self.format_duration(total_duration)}")
        print(f"{'='*60}\n")
        
        # Print turn-by-turn directions
        print(f"{'='*60}")
        print(f"🧭 TURN-BY-TURN DIRECTIONS")
        print(f"{'='*60}\n")
        
        steps = route['legs'][0]['steps']
        for i, step in enumerate(steps, 1):
            instruction = self.format_instruction(step, i)
            print(instruction)
            print()
        
        print(f"{'='*60}")
        print(f"✅ You have arrived at your destination!")
        print(f"{'='*60}\n")
    
    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates in meters using Haversine formula
        
        Args:
            coord1: (latitude, longitude) of first point
            coord2: (latitude, longitude) of second point
            
        Returns:
            Distance in meters
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Radius of Earth in meters
        R = 6371000
        
        # Convert to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def find_current_step(self, current_location: Tuple[float, float], steps: List[Dict]) -> int:
        """
        Find which step the user is currently on based on their location
        
        Args:
            current_location: (latitude, longitude) of current position
            steps: List of route steps
            
        Returns:
            Index of the current step
        """
        min_distance = float('inf')
        current_step_idx = 0
        
        for i, step in enumerate(steps):
            # Get the maneuver location for this step
            maneuver_location = step['maneuver']['location']
            step_coords = (maneuver_location[1], maneuver_location[0])  # lon,lat -> lat,lon
            
            distance = self.calculate_distance(current_location, step_coords)
            
            if distance < min_distance:
                min_distance = distance
                current_step_idx = i
        
        return current_step_idx
    
    def live_navigation(self, destination: str, update_interval: int = 5):
        """
        Provide live turn-by-turn navigation based on current location
        
        Args:
            destination: Destination address
            update_interval: How often to update location (seconds)
        """
        print(f"\n{'='*60}")
        print(f"🧭 LIVE NAVIGATION MODE")
        print(f"{'='*60}")
        print(f"Destination: 📍 {destination}")
        print(f"Update interval: {update_interval} seconds")
        print(f"{'='*60}\n")
        
        # Get destination coordinates
        print("🔍 Finding destination...")
        dest_coords = self.geocode(destination)
        if not dest_coords:
            print(f"❌ Could not find destination: {destination}")
            return
        
        print(f"✓ Destination: {dest_coords[0]:.4f}, {dest_coords[1]:.4f}\n")
        
        # Get initial location
        print("📍 Detecting your current location...")
        current_location = self.get_current_location()
        if not current_location:
            print("❌ Could not detect current location")
            return
        
        print(f"✓ Current location: {current_location[0]:.4f}, {current_location[1]:.4f}\n")
        
        # Calculate initial route
        print("🗺️  Calculating route...\n")
        route_data = self.get_route(current_location, dest_coords)
        
        if not route_data or not route_data.get('routes'):
            print("❌ Could not find a route")
            return
        
        route = route_data['routes'][0]
        steps = route['legs'][0]['steps']
        total_distance = route['distance']
        
        print(f"{'='*60}")
        print(f"📊 ROUTE OVERVIEW")
        print(f"{'='*60}")
        print(f"Total Distance: {self.format_distance(total_distance)}")
        print(f"Total Steps: {len(steps)}")
        print(f"{'='*60}\n")
        
        print("🚶 Starting live navigation...")
        print("Press Ctrl+C to stop\n")
        print(f"{'='*60}\n")
        
        current_step_idx = 0
        last_step_idx = -1
        
        try:
            iteration = 0
            while current_step_idx < len(steps):
                iteration += 1
                
                # Get fresh GPS location on each update
                print(f"\n🔄 Update #{iteration} - Getting current location...")
                current_location = self.get_current_location()
                if not current_location:
                    print("⚠️  Could not update location, retrying...")
                    time.sleep(update_interval)
                    continue
                
                # Calculate distance to destination
                distance_to_dest = self.calculate_distance(current_location, dest_coords)
                
                # Check if we've arrived (within 20 meters)
                if distance_to_dest < 20:
                    print("\n" + "="*60)
                    print("🎯 YOU HAVE ARRIVED AT YOUR DESTINATION!")
                    print("="*60 + "\n")
                    break
                
                # Find current step based on location
                current_step_idx = self.find_current_step(current_location, steps)
                
                # Display current status (always show, not just on step change)
                step = steps[current_step_idx]
                instruction = self.format_instruction(step, current_step_idx + 1)
                
                # Calculate distance to next maneuver
                maneuver_location = step['maneuver']['location']
                maneuver_coords = (maneuver_location[1], maneuver_location[0])
                distance_to_maneuver = self.calculate_distance(current_location, maneuver_coords)
                
                # Clear screen for better readability (optional)
                print("\n" + "="*60)
                print(f"📍 Current Position: {current_location[0]:.4f}, {current_location[1]:.4f}")
                print(f"📏 Distance to destination: {self.format_distance(distance_to_dest)}")
                print(f"📏 Distance to next turn: {self.format_distance(distance_to_maneuver)}")
                print(f"\n🧭 CURRENT INSTRUCTION (Step {current_step_idx + 1}/{len(steps)}):")
                print(instruction)
                
                # Show next instruction if available
                if current_step_idx + 1 < len(steps):
                    next_step = steps[current_step_idx + 1]
                    next_instruction = self.format_instruction(next_step, current_step_idx + 2)
                    print(f"\n⏭️  NEXT:")
                    print(next_instruction)
                
                # Alert if step changed
                if current_step_idx != last_step_idx and last_step_idx != -1:
                    print(f"\n✅ Completed step {last_step_idx + 1}! Moving to step {current_step_idx + 1}")
                
                last_step_idx = current_step_idx
                print("="*60)
                
                # Wait before next update
                print(f"\n⏳ Next update in {update_interval} seconds... (Press Ctrl+C to stop)")
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Navigation stopped by user")
            print(f"Last known position: {current_location[0]:.4f}, {current_location[1]:.4f}\n")


def main():
    """Main function to run the text-based navigation system"""
    print("\n" + "="*60)
    print("🚶 TEXT MAPS - Walking Navigation System")
    print("="*60 + "\n")
    
    # Check for mode argument
    mode = 'walking'  # Default to walking
    live_mode = False
    update_interval = 5
    args = sys.argv[1:]
    
    # Check if user specified live mode
    if '--live' in args:
        live_mode = True
        args.remove('--live')
    
    # Check for update interval
    if '--interval' in args:
        interval_idx = args.index('--interval')
        if interval_idx + 1 < len(args):
            try:
                update_interval = int(args[interval_idx + 1])
                args = args[:interval_idx] + args[interval_idx + 2:]
            except ValueError:
                print("❌ Invalid interval value")
                return
    
    # Check if user specified a mode
    if '--mode' in args:
        mode_idx = args.index('--mode')
        if mode_idx + 1 < len(args):
            mode = args[mode_idx + 1]
            # Remove mode arguments
            args = args[:mode_idx] + args[mode_idx + 2:]
    
    # Validate mode
    valid_modes = ['walking', 'driving', 'cycling']
    if mode not in valid_modes:
        print(f"❌ Invalid mode: {mode}")
        print(f"Valid modes: {', '.join(valid_modes)}")
        return
    
    navigator = TextMaps(mode=mode)
    
    # Live navigation mode
    if live_mode:
        if len(args) >= 1:
            destination = args[0]
        else:
            destination = input("Enter destination: ").strip()
            if not destination:
                print("❌ Destination cannot be empty")
                return
        
        navigator.live_navigation(destination, update_interval)
        return
    
    # Standard navigation mode
    # Get user input
    if len(args) >= 2:
        # Use command line arguments
        start = args[0]
        end = args[1]
    else:
        # Interactive mode
        print("Enter your route details:\n")
        start = input("Starting location (or 'current'): ").strip()
        if not start:
            print("❌ Starting location cannot be empty")
            return
        
        end = input("Destination (or 'current'): ").strip()
        if not end:
            print("❌ Destination cannot be empty")
            return
    
    # Get and display directions
    navigator.print_directions(start, end)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Navigation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

