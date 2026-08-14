"# color_tracker/tracker.py
import cv2
import numpy as np

class DroneTracker:
    \"\"\"
    Stereo colour-based object tracker for two drones.
    Provides 3D position estimation based on two camera feeds.
    \"\"\"

    def __init__(self, baseline=2.0, focal_length=600.0, cam0_idx=0, cam1_idx=1):
        self.baseline = baseline
        self.focal_length = focal_length
        
        # Initialize cameras
        self.cap_left = cv2.VideoCapture(cam0_idx)
        self.cap_right = cv2.VideoCapture(cam1_idx)

        if not self.cap_left.isOpened() or not self.cap_right.isOpened():
            raise RuntimeError(\"Unable to open one or both webcams.\")

        # HSV Ranges
        self.color_presets = {
            \"orange\": {
                \"lower\": np.array([0, 0, 88], dtype=np.uint8),
                \"upper\": np.array([90, 150, 255], dtype=np.uint8),
            },
            \"yellow\": {
                \"lower\": np.array([0, 96, 0], dtype=np.uint8),
                \"upper\": np.array([19, 222, 232], dtype=np.uint8),
            },
        }

    def _get_mask(self, hsv_frame, lower, upper):
        mask = cv2.inRange(hsv_frame, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
        return mask

    def _find_object_center(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            biggest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(biggest) > 500:
                (x, y), _ = cv2.minEnclosingCircle(biggest)
                return (int(x), int(y))
        return None

    def _estimate_3d_position(self, left_center, right_center, center_x):
        if left_center is None or right_center is None:
            return None

        disparity = left_center[0] - right_center[0]
        if disparity == 0:
            return None

        # Z = (f * B) / disparity
        z = (self.focal_length * self.baseline) / disparity
        # X = (x_left - cx) * Z / f
        x = (left_center[0] - center_x) * z / self.focal_length
        # Y estimation (simplified)
        y = 0 
        
        return (x, y, z)

    def update(self):
        \"\"\"
        Captures frames and returns the 3D positions of the detected drones.
        Returns: dict { 'yellow': (x,y,z) or None, 'orange': (x,y,z) or None }
        \"\"\"
        ret_l, frame_l = self.cap_left.read()
        ret_r, frame_r = self.cap_right.read()

        if not ret_l or not ret_r:
            return None

        hsv_l = cv2.cvtColor(frame_l, cv2.COLOR_BGR2HSV)
        hsv_r = cv2.cvtColor(frame_r, cv2.COLOR_BGR2HSV)

        height, width, _ = frame_l.shape
        center_x = width // 2

        results = {}
        for color_name, range_vals in self.color_presets.items():
            mask_l = self._get_mask(hsv_l, range_vals[\"lower\"], range_vals[\"upper\"])
            mask_r = self._get_mask(hsv_r, range_vals[\"lower\"], range_vals[\"upper\"])

            center_l = self._find_object_center(mask_l)
            center_r = self._find_object_center(mask_r)

            pos_3d = self._estimate_3d_position(center_l, center_r, center_x)
            results[color_name] = pos_3d

        return results

    def release(self):
        self.cap_left.release()
        self.cap_right.release()
"
