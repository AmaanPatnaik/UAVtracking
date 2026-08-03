import cv2
import numpy as np
from typing import Tuple, Optional

class DroneDetector:
    """
    Handles target detection using OpenCV.
    Designed to be easily swappable with an ML model (e.g. YOLOv8).
    """
    def __init__(self, config: dict):
        self.config = config
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['vision']['camera_width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['vision']['camera_height'])

    def get_target(self, color_name: str = "red") -> Tuple[Optional[Tuple[int, int]], np.ndarray]:
        """
        Detects the target color and returns the center coordinates and the frame.
        Returns: ((x, y), frame) or (None, frame)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, np.array([])

        # Convert to HSV for robust color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Load ranges from config
        lower = np.array(self.config['colors'][color_name]['lower'], dtype=np.uint8)
        upper = np.array(self.config['colors'][color_name]['upper'], dtype=np.uint8)
        
        # Create mask and clean noise
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((5,5), np.uint8))
        
        # Find contours and pick the largest one
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            biggest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(biggest) > 500:
                (x, y), radius = cv2.minEnclosingCircle(biggest)
                return (int(x), int(y)), frame
        
        return None, frame

    def release(self):
        self.cap.release()