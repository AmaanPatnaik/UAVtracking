import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict

class DroneDetector:
    \"\"\"
    Handles target detection using dual-camera stereo vision.
    Tracks multiple drones based on HSV color values.
    \"\"\"
    def __init__(self, config: dict):
        self.config = config
        self.camera_indices = config['vision'].get('camera_indices', [0])
        self.baseline = config['vision'].get('baseline_feet', 2.0)
        self.caps = []
        
        for idx in self.camera_indices:
            cap = cv2.VideoCapture(idx)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['vision']['camera_width'])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['vision']['camera_height'])
            self.caps.append(cap)

    def _detect_color(self, frame, color_name: str) -> Optional[Tuple[int, int]]:
        \"\"\"Internal helper to find the center of a specific color in a frame.\"\"\"
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array(self.config['colors'][color_name]['lower'], dtype=np.uint8)
        upper = np.array(self.config['colors'][color_name]['upper'], dtype=np.uint8)
        
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((5,5), np.uint8))
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            biggest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(biggest) > 500:
                (x, y), _ = cv2.minEnclosingCircle(biggest)
                return (int(x), int(y))
        return None

    def get_targets(self, colors: List[str] = [\"yellow\", \"orange\"]) -> Dict[str, Dict]:
        \"\"\"
        Detects multiple targets across all cameras.
        Returns a dictionary mapping color -> { 'center': (x,y), 'depth': z, 'frame': frame }
        (Center is averaged across cameras for tracking)
        \"\"\"
        frames = []
        for cap in self.caps:
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
            else:
                frames.append(None)

        if not frames or frames[0] is None:
            return {}

        results = {}
        for color in colors:
            detections = []
            for frame in frames:
                if frame is not None:
                    pos = self._detect_color(frame, color)
                    if pos:
                        detections.append(pos)
            
            if detections:
                # Average center across cameras for the turret to track
                avg_x = int(sum(d[0] for d in detections) / len(detections))
                avg_y = int(sum(d[1] for d in detections) / len(detections))
                
                # Basic Stereo Depth Calculation: z = (f * baseline) / disparity
                depth = None
                if len(detections) >= 2:
                    disparity = abs(detections[0][0] - detections[1][0])
                    if disparity > 0:
                        # Simplified depth estimate (pixels_per_degree * baseline)
                        # Real depth requires focal length f, using config as proxy
                        f_px = self.config['vision']['pixels_per_degree_h'] * 57.3 
                        depth = (f_px * self.baseline) / disparity
                
                results[color] = {
                    'center': (avg_x, avg_y),
                    'depth': depth,
                    'frame': frames[0] # Return first frame for visualization
                }
        
        return results

    def release(self):
        for cap in self.caps:
            cap.release()"
