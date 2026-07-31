# color_tracker/tracker_fixed.py
"""Simple colour‑based object tracker using the built‑in webcam.

Features
--------
* Detects a single colour (red or blue) based on HSV thresholds.
* Optional ``--color`` argument to choose red or blue.
* Optional ``--tune`` argument opens HSV trackbars for live tweaking.
* Shows the webcam feed with a circle around the detected object and a binary mask.
"""

import argparse
import cv2
import numpy as np
import os

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def load_color_presets(_: str = None) -> dict:
    """Return hard‑coded HSV ranges for red and blue.
    The argument is ignored; it exists only for backward compatibility.
    """
    return {
        "red": {
            "lower": np.array([0, 120, 70], dtype=np.uint8),
            "upper": np.array([10, 255, 255], dtype=np.uint8),
        },
        "blue": {
            "lower": np.array([100, 150, 0], dtype=np.uint8),
            "upper": np.array([140, 255, 255], dtype=np.uint8),
        },
    }

def get_mask(hsv_frame: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    """Return a cleaned binary mask for the given HSV range."""
    mask = cv2.inRange(hsv_frame, lower, upper)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
    return mask

def create_hsv_trackbars(window_name: str, lower: np.ndarray, upper: np.ndarray) -> None:
    """Create six trackbars (L‑H, L‑S, L‑V, U‑H, U‑S, U‑V) for HSV tuning."""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("L‑H", window_name, int(lower[0]), 179, lambda _: None)
    cv2.createTrackbar("L‑S", window_name, int(lower[1]), 255, lambda _: None)
    cv2.createTrackbar("L‑V", window_name, int(lower[2]), 255, lambda _: None)
    cv2.createTrackbar("U‑H", window_name, int(upper[0]), 179, lambda _: None)
    cv2.createTrackbar("U‑S", window_name, int(upper[1]), 255, lambda _: None)
    cv2.createTrackbar("U‑V", window_name, int(upper[2]), 255, lambda _: None)

def read_hsv_from_trackbars(window_name: str) -> tuple[np.ndarray, np.ndarray]:
    """Read current HSV values from the trackbars and return (lower, upper)."""
    lower = np.array([
        cv2.getTrackbarPos("L‑H", window_name),
        cv2.getTrackbarPos("L‑S", window_name),
        cv2.getTrackbarPos("L‑V", window_name)
    ], dtype=np.uint8)
    upper = np.array([
        cv2.getTrackbarPos("U‑H", window_name),
        cv2.getTrackbarPos("U‑S", window_name),
        cv2.getTrackbarPos("U‑V", window_name)
    ], dtype=np.uint8)
    return lower, upper

# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Colour‑based object tracker (red/blue).")
    parser.add_argument("--color", default="red", choices=["red", "blue"],
                        help="Colour preset to track (default: red)")
    parser.add_argument("--tune", action="store_true",
                        help="Show HSV trackbars for live tuning")
    args = parser.parse_args()

    # Load colour presets (hard‑coded)
    color_presets = load_color_presets()
    if args.color not in color_presets:
        raise ValueError(f"Colour '{args.color}' not recognised.")

    lower_hsv = color_presets[args.color]["lower"].copy()
    upper_hsv = color_presets[args.color]["upper"].copy()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Unable to open webcam (device 0).")

    if args.tune:
        create_hsv_trackbars("HSV‑Tuner", lower_hsv, upper_hsv)

    print(f"Tracking colour: {args.color} (press ESC to quit)")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame capture failed – exiting.")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        if args.tune:
            lower_hsv, upper_hsv = read_hsv_from_trackbars("HSV‑Tuner")

        mask = get_mask(hsv, lower_hsv, upper_hsv)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            biggest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(biggest) > 500:
                (x, y), radius = cv2.minEnclosingCircle(biggest)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(frame, center, radius, (0, 255, 0), 2)   # green outline
                cv2.circle(frame, center, 5, (0, 0, 255), -1)      # red centre dot
                print(f"Object centre: ({center[0]}, {center[1]})")

        cv2.imshow("Webcam", frame)
        cv2.imshow("Mask", mask)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
