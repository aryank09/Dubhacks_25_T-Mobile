#!/usr/bin/env python3
"""
GPS Server for Raspberry Pi
Receives GPS coordinates from computer and serves them to navigation system
"""

from flask import Flask, request, jsonify
import time
import threading
from typing import Optional, Tuple
import json


class GPSServer:
    """Simple server to receive and store GPS coordinates"""
    
    def __init__(self, port: int = 5000):
        """
        Initialize GPS server
        
        Args:
            port: Port to run server on
        """
        self.app = Flask(__name__)
        self.port = port
        self.current_location = None
        self.last_update = None
        self.lock = threading.Lock()
        
        # Setup routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/location', methods=['POST'])
        def receive_location():
            """Receive GPS coordinates from computer"""
            try:
                data = request.get_json()
                
                if not data or 'latitude' not in data or 'longitude' not in data:
                    return jsonify({'error': 'Invalid data format'}), 400
                
                lat = float(data['latitude'])
                lon = float(data['longitude'])
                timestamp = data.get('timestamp', time.time())
                
                with self.lock:
                    self.current_location = (lat, lon)
                    self.last_update = timestamp
                
                print(f"📍 Received location: {lat:.4f}, {lon:.4f}")
                return jsonify({'status': 'success', 'message': 'Location received'})
                
            except Exception as e:
                print(f"❌ Error receiving location: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/location', methods=['GET'])
        def get_location():
            """Get current GPS coordinates"""
            try:
                with self.lock:
                    if self.current_location is None:
                        return jsonify({'error': 'No location available'}), 404
                    
                    return jsonify({
                        'latitude': self.current_location[0],
                        'longitude': self.current_location[1],
                        'timestamp': self.last_update,
                        'age_seconds': time.time() - self.last_update if self.last_update else None
                    })
                    
            except Exception as e:
                print(f"❌ Error getting location: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Get server status"""
            try:
                with self.lock:
                    has_location = self.current_location is not None
                    age_seconds = None
                    
                    if has_location and self.last_update:
                        age_seconds = time.time() - self.last_update
                    
                    return jsonify({
                        'server_running': True,
                        'has_location': has_location,
                        'last_update': self.last_update,
                        'age_seconds': age_seconds,
                        'location': self.current_location
                    })
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current GPS location from server
        
        Returns:
            Tuple of (latitude, longitude) or None if not available
        """
        with self.lock:
            return self.current_location
    
    def is_location_fresh(self, max_age_seconds: int = 30) -> bool:
        """
        Check if location is fresh (not too old)
        
        Args:
            max_age_seconds: Maximum age in seconds before considering stale
            
        Returns:
            bool: True if location is fresh, False otherwise
        """
        if self.current_location is None or self.last_update is None:
            return False
        
        age = time.time() - self.last_update
        return age <= max_age_seconds
    
    def get_local_ip(self) -> str:
        """Get the local IP address of this device"""
        import socket
        try:
            # Connect to a remote address to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "localhost"

    def run(self, host: str = '0.0.0.0', debug: bool = False):
        """
        Run the GPS server
        
        Args:
            host: Host to bind to (0.0.0.0 for all interfaces)
            debug: Enable Flask debug mode
        """
        # Get the actual IP address for display
        actual_ip = self.get_local_ip()
        
        print(f"\n{'='*60}")
        print(f"🌐 GPS SERVER STARTING")
        print(f"{'='*60}")
        print(f"🖥️  Raspberry Pi GPS Server")
        print(f"🌐 Server URL: http://{actual_ip}:{self.port}")
        print(f"📡 Waiting for GPS coordinates from computer...")
        print(f"💡 Computer should connect to: http://{actual_ip}:{self.port}")
        print(f"{'='*60}\n")
        
        try:
            self.app.run(host=host, port=self.port, debug=debug, threaded=True)
        except KeyboardInterrupt:
            print("\n\n⏹️  GPS server stopped by user")
        except Exception as e:
            print(f"\n❌ Server error: {e}")


def main():
    """Main function to run GPS server"""
    print("\n" + "="*60)
    print("🌐 RASPBERRY PI GPS SERVER")
    print("="*60 + "\n")
    
    # Create and run server
    server = GPSServer(port=5000)
    server.run(host='0.0.0.0', debug=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 GPS server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
