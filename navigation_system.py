#!/usr/bin/env python3
"""
Navigation System with GPS Integration
Handles location tracking and route guidance
"""

import logging
from typing import Optional, Tuple, List
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NavigationSystem:
    def __init__(self):
        """Initialize navigation system"""
        self.geocoder = Nominatim(user_agent="blind_navigation_assistant")
        self.current_location = None
        self.destination = None
        self.route = []
        
        # Try to connect to GPS daemon (gpsd)
        self.gps_available = self._check_gps()
    
    def _check_gps(self) -> bool:
        """Check if GPS is available"""
        try:
            from gps import gps, WATCH_ENABLE
            self.gps_session = gps(mode=WATCH_ENABLE)
            logger.info("GPS connection established")
            return True
        except Exception as e:
            logger.warning(f"GPS not available: {e}")
            return False
    
    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current GPS coordinates
        Returns:
            Tuple of (latitude, longitude) or None if unavailable
        """
        if self.gps_available:
            try:
                report = self.gps_session.next()
                if report['class'] == 'TPV':
                    if hasattr(report, 'lat') and hasattr(report, 'lon'):
                        self.current_location = (report.lat, report.lon)
                        logger.info(f"Current location: {self.current_location}")
                        return self.current_location
            except Exception as e:
                logger.error(f"Error reading GPS: {e}")
        
        return self.current_location
    
    def set_current_location(self, lat: float, lon: float):
        """Manually set current location (for testing without GPS)"""
        self.current_location = (lat, lon)
        logger.info(f"Location set to: {self.current_location}")
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates
        Args:
            address: Street address or place name
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            location = self.geocoder.geocode(address)
            if location:
                logger.info(f"Geocoded '{address}' to {location.latitude}, {location.longitude}")
                return (location.latitude, location.longitude)
            else:
                logger.warning(f"Could not geocode address: {address}")
                return None
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to address
        Args:
            lat, lon: GPS coordinates
        Returns:
            Address string or None if not found
        """
        try:
            location = self.geocoder.reverse(f"{lat}, {lon}")
            if location:
                logger.info(f"Reverse geocoded to: {location.address}")
                return location.address
            return None
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None
    
    def calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """
        Calculate distance between two points in meters
        Args:
            point1, point2: Tuples of (latitude, longitude)
        Returns:
            Distance in meters
        """
        distance = geodesic(point1, point2).meters
        return distance
    
    def get_bearing(self, point1: Tuple[float, float], 
                   point2: Tuple[float, float]) -> str:
        """
        Get compass direction from point1 to point2
        Args:
            point1, point2: Tuples of (latitude, longitude)
        Returns:
            Direction string (N, NE, E, SE, S, SW, W, NW)
        """
        import math
        
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlon = lon2 - lon1
        
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.degrees(math.atan2(x, y))
        bearing = (bearing + 360) % 360
        
        # Convert to compass direction
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round(bearing / 45) % 8
        
        return directions[index]
    
    def set_destination(self, destination: str) -> bool:
        """
        Set navigation destination
        Args:
            destination: Address or place name
        Returns:
            True if destination was set successfully
        """
        coords = self.geocode_address(destination)
        if coords:
            self.destination = coords
            logger.info(f"Destination set to: {destination}")
            return True
        return False
    
    def get_navigation_instruction(self) -> Optional[str]:
        """
        Get navigation instruction from current location to destination
        Returns:
            Human-readable navigation instruction
        """
        if not self.current_location or not self.destination:
            return None
        
        distance = self.calculate_distance(self.current_location, self.destination)
        bearing = self.get_bearing(self.current_location, self.destination)
        
        # Format distance
        if distance < 1000:
            distance_str = f"{int(distance)} meters"
        else:
            distance_str = f"{distance/1000:.1f} kilometers"
        
        instruction = f"Head {bearing} for {distance_str} to reach your destination."
        
        # Add more specific instructions if close
        if distance < 50:
            instruction = f"You are very close to your destination, about {int(distance)} meters away."
        elif distance < 10:
            instruction = "You have arrived at your destination."
        
        return instruction
    
    def search_nearby(self, query: str, radius: int = 1000) -> List[Dict]:
        """
        Search for nearby places (requires OpenStreetMap Nominatim)
        Args:
            query: Type of place (e.g., "coffee shop", "bus stop")
            radius: Search radius in meters
        Returns:
            List of nearby places with details
        """
        if not self.current_location:
            return []
        
        try:
            # Search near current location
            lat, lon = self.current_location
            locations = self.geocoder.geocode(
                query,
                exactly_one=False,
                limit=5,
                addressdetails=True,
                viewbox=(lon-0.01, lat-0.01, lon+0.01, lat+0.01),
                bounded=True
            )
            
            results = []
            if locations:
                for loc in locations:
                    distance = self.calculate_distance(
                        self.current_location,
                        (loc.latitude, loc.longitude)
                    )
                    if distance <= radius:
                        results.append({
                            'name': loc.address,
                            'coordinates': (loc.latitude, loc.longitude),
                            'distance': distance
                        })
            
            # Sort by distance
            results.sort(key=lambda x: x['distance'])
            return results
            
        except Exception as e:
            logger.error(f"Error searching nearby: {e}")
            return []


if __name__ == "__main__":
    # Test navigation system
    nav = NavigationSystem()
    
    # Test with example location (Seattle)
    nav.set_current_location(47.6062, -122.3321)
    
    address = nav.reverse_geocode(47.6062, -122.3321)
    print(f"Current address: {address}")
    
    # Set destination
    if nav.set_destination("Space Needle, Seattle"):
        instruction = nav.get_navigation_instruction()
        print(f"Navigation: {instruction}")

