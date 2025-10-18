#!/usr/bin/env python3
"""
Obstacle Detection using Camera
Uses OpenCV for basic obstacle detection
"""

import cv2
import numpy as np
import logging
from typing import List, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObstacleDetector:
    def __init__(self, use_pi_camera=True):
        """
        Initialize obstacle detector
        Args:
            use_pi_camera: If True, use Raspberry Pi camera, else use USB camera
        """
        self.use_pi_camera = use_pi_camera
        self.camera = None
        self.last_frame = None
        
        self._init_camera()
    
    def _init_camera(self):
        """Initialize camera"""
        try:
            if self.use_pi_camera:
                # Try to use Raspberry Pi camera
                try:
                    from picamera2 import Picamera2
                    self.camera = Picamera2()
                    config = self.camera.create_still_configuration()
                    self.camera.configure(config)
                    self.camera.start()
                    logger.info("Raspberry Pi camera initialized")
                except ImportError:
                    logger.warning("picamera2 not available, falling back to OpenCV")
                    self.use_pi_camera = False
                    self.camera = cv2.VideoCapture(0)
            else:
                # Use USB camera with OpenCV
                self.camera = cv2.VideoCapture(0)
                if self.camera.isOpened():
                    logger.info("USB camera initialized")
                else:
                    logger.error("Failed to open camera")
                    self.camera = None
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            self.camera = None
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera
        Returns:
            Numpy array of the image or None if capture failed
        """
        if not self.camera:
            return None
        
        try:
            if self.use_pi_camera:
                # Capture from Pi camera
                frame = self.camera.capture_array()
            else:
                # Capture from USB camera
                ret, frame = self.camera.read()
                if not ret:
                    logger.error("Failed to capture frame")
                    return None
            
            self.last_frame = frame
            return frame
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def detect_edges(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect edges in the frame using Canny edge detection
        Args:
            frame: Input image
        Returns:
            Edge-detected image
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        return edges
    
    def detect_obstacles(self) -> List[str]:
        """
        Detect obstacles in current view
        Returns:
            List of detected obstacles/objects
        """
        frame = self.capture_frame()
        if frame is None:
            return []
        
        obstacles = []
        
        # Simple obstacle detection based on image analysis
        # This is a basic implementation - for better results, use ML models
        
        edges = self.detect_edges(frame)
        
        # Count edge density in different regions
        h, w = edges.shape
        regions = {
            'left': edges[:, :w//3],
            'center': edges[:, w//3:2*w//3],
            'right': edges[:, 2*w//3:]
        }
        
        for region_name, region in regions.items():
            edge_density = np.sum(region > 0) / region.size
            
            if edge_density > 0.1:  # Threshold for obstacle detection
                obstacles.append(f"obstacle on {region_name}")
        
        # Detect motion (compare with previous frame if available)
        # This helps identify moving objects
        if self.last_frame is not None:
            gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_last = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2GRAY)
            
            diff = cv2.absdiff(gray_current, gray_last)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            motion_density = np.sum(thresh > 0) / thresh.size
            if motion_density > 0.05:
                obstacles.append("moving object detected")
        
        self.last_frame = frame
        return obstacles
    
    def get_distance_estimate(self) -> Optional[str]:
        """
        Estimate distance to nearest obstacle
        Returns:
            Distance category (very close, close, moderate, far)
        """
        frame = self.capture_frame()
        if frame is None:
            return None
        
        edges = self.detect_edges(frame)
        
        # Check bottom third of image (closest to user)
        h, w = edges.shape
        bottom_third = edges[2*h//3:, :]
        
        edge_density = np.sum(bottom_third > 0) / bottom_third.size
        
        if edge_density > 0.2:
            return "very close"
        elif edge_density > 0.1:
            return "close"
        elif edge_density > 0.05:
            return "moderate distance"
        else:
            return "far or no obstacles"
    
    def describe_scene(self) -> str:
        """
        Generate a simple description of the current scene
        Returns:
            Text description of what the camera sees
        """
        obstacles = self.detect_obstacles()
        distance = self.get_distance_estimate()
        
        if not obstacles:
            return f"Path appears clear ahead. Objects are {distance}."
        else:
            obstacle_list = ", ".join(obstacles)
            return f"Detected: {obstacle_list}. Distance: {distance}."
    
    def cleanup(self):
        """Release camera resources"""
        if self.camera:
            if self.use_pi_camera:
                self.camera.stop()
            else:
                self.camera.release()
            logger.info("Camera released")


if __name__ == "__main__":
    # Test obstacle detection
    detector = ObstacleDetector(use_pi_camera=False)
    
    print("Testing obstacle detection...")
    for i in range(5):
        description = detector.describe_scene()
        print(f"Scene {i+1}: {description}")
        time.sleep(1)
    
    detector.cleanup()

