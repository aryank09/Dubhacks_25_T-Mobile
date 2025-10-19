#!/usr/bin/env python3
"""
GPS Sender for Computer
Sends GPS coordinates to localhost server for Raspberry Pi navigation
"""

import requests
import time
import json
import sys
from typing import Optional, Tuple
import geocoder
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse
import webbrowser


class GPSSender:
    """Sends GPS coordinates to localhost server"""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        """
        Initialize GPS sender
        
        Args:
            server_url: URL of the localhost server to send coordinates to
        """
        self.server_url = server_url
        self.update_interval = 5  # Send coordinates every 5 seconds
        
    def get_gps_location_from_browser(self) -> Optional[Tuple[float, float]]:
        """
        Get precise GPS location using browser-based geolocation API
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
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
                        <head><title>GPS Location Sender</title></head>
                        <body>
                        <h2>📍 GPS Location Sender</h2>
                        <p id="status">Requesting location permission...</p>
                        <p>This will send your location to the Raspberry Pi navigation system.</p>
                        <script>
                        if (navigator.geolocation) {
                            navigator.geolocation.getCurrentPosition(
                                function(position) {
                                    document.getElementById('status').textContent = 'Location acquired! Sending to server...';
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
            server = HTTPServer(('localhost', 8889), LocationHandler)
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            
            # Open browser
            print("🌐 Opening browser to get your precise GPS location...")
            print("   Please allow location access when prompted.")
            webbrowser.open('http://localhost:8889')
            
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
    
    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current location using GPS or IP-based geolocation
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Try browser-based GPS (most accurate)
            location = self.get_gps_location_from_browser()
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
    
    def send_location(self, lat: float, lon: float) -> bool:
        """
        Send GPS coordinates to the server
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = {
                'latitude': lat,
                'longitude': lon,
                'timestamp': time.time()
            }
            
            response = requests.post(
                f"{self.server_url}/location",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Sent location: {lat:.4f}, {lon:.4f}")
                return True
            else:
                print(f"❌ Failed to send location: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure the server is running.")
            return False
        except Exception as e:
            print(f"❌ Error sending location: {e}")
            return False
    
    def run_continuous_sending(self):
        """Continuously send GPS coordinates to server"""
        print(f"\n{'='*60}")
        print(f"📡 GPS LOCATION SENDER")
        print(f"{'='*60}")
        print(f"🖥️  Computer GPS → Raspberry Pi Navigation")
        print(f"🔄 Update interval: {self.update_interval} seconds")
        print(f"🌐 Server URL: {self.server_url}")
        print(f"{'='*60}\n")
        
        # Get initial location
        print("📍 Getting initial GPS location...")
        location = self.get_current_location()
        if not location:
            print("❌ Could not get GPS location")
            return
        
        lat, lon = location
        print(f"✅ Initial location: {lat:.4f}, {lon:.4f}")
        
        # Test server connection
        print(f"\n🔗 Testing connection to server...")
        if not self.send_location(lat, lon):
            print("❌ Could not connect to server. Please make sure the server is running on the Raspberry Pi.")
            return
        
        print("✅ Server connection successful!")
        print(f"\n🚀 Starting continuous GPS sending...")
        print("Press Ctrl+C to stop\n")
        
        try:
            iteration = 0
            while True:
                iteration += 1
                
                # Get current location
                print(f"\n🔄 Update #{iteration} - Getting current location...")
                location = self.get_current_location()
                
                if location:
                    lat, lon = location
                    print(f"📍 Current location: {lat:.4f}, {lon:.4f}")
                    
                    # Send to server
                    if self.send_location(lat, lon):
                        print("✅ Location sent successfully")
                    else:
                        print("⚠️  Failed to send location")
                else:
                    print("⚠️  Could not get current location")
                
                # Wait before next update
                print(f"⏳ Next update in {self.update_interval} seconds...")
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  GPS sending stopped by user")
            print("📍 Last sent location will remain available on server")


def main():
    """Main function to run GPS sender"""
    print("\n" + "="*60)
    print("📡 COMPUTER GPS SENDER")
    print("="*60 + "\n")
    
    # Check if server URL is provided as argument
    server_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
        print(f"🌐 Using custom server URL: {server_url}")
    else:
        print(f"🌐 Using default server URL: {server_url}")
        print("   (You can specify a custom URL as an argument)")
        print("   Example: python gps_sender.py http://192.168.1.100:5000")
    
    # Create GPS sender
    gps_sender = GPSSender(server_url)
    
    # Run continuous sending
    gps_sender.run_continuous_sending()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 GPS sender stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
