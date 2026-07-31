
# tracker.py
"""Simple colour‑based object tracker using the built‑in webcam.

Features
--------
* Detects a single colour (red or blue) using hard‑coded HSV presets.
* ``--rgb`` opens three sliders (R‑G‑B) and converts the chosen colour to HSV.
* ``--click`` lets you click a pixel in the video – the colour under the cursor
  becomes the tracking target.
* ``--tune`` opens the original HSV sliders for fine‑tuning.
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
    The argument is ignored – kept for backward compatibility.
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
    mask = cv2.inRange(hsv_frame, lower, upper)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
    return mask

def create_hsv_trackbars(name: str, lower: np.ndarray, upper: np.ndarray) -> None:
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("L‑H", name, int(lower[0]), 179, lambda _: None)
    cv2.createTrackbar("L‑S", name, int(lower[1]), 255, lambda _: None)
    cv2.createTrackbar("L‑V", name, int(lower[2]), 255, lambda _: None)
    cv2.createTrackbar("U‑H", name, int(upper[0]), 179, lambda _: None)
    cv2.createTrackbar("U‑S", name, int(upper[1]), 255, lambda _: None)
    cv2.createTrackbar("U‑V", name, int(upper[2]), 255, lambda _: None)

def read_hsv_from_trackbars(name: str) -> tuple[np.ndarray, np.ndarray]:
    lower = np.array([
        cv2.getTrackbarPos("L‑H", name),
        cv2.getTrackbarPos("L‑S", name),
        cv2.getTrackbarPos("L‑V", name)
    ], dtype=np.uint8)
    upper = np.array([
        cv2.getTrackbarPos("U‑H", name),
        cv2.getTrackbarPos("U‑S", name),
        cv2.getTrackbarPos("U‑V", name)
    ], dtype=np.uint8)
    return lower, upper

def create_rgb_trackbars(name: str, rgb: np.ndarray) -> None:
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("R", name, int(rgb[0]), 255, lambda _: None)
    cv2.createTrackbar("G", name, int(rgb[1]), 255, lambda _: None)
    cv2.createTrackbar("B", name, int(rgb[2]), 255, lambda _: None)

def read_rgb_from_trackbars(name: str) -> np.ndarray:
    r = cv2.getTrackbarPos("R", name)
    g = cv2.getTrackbarPos("G", name)
    b = cv2.getTrackbarPos("B", name)
    return np.array([r, g, b], dtype=np.uint8)

# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Colour‑based tracker (red/blue).")
    parser.add_argument("--color", default="red", choices=["red", "blue"],
                        help="Preset colour to track (default: red)")
    parser.add_argument("--tune", action="store_true",
                        help="Show HSV trackbars for live tuning")
    parser.add_argument("--rgb", action="store_true",
                        help="Open RGB sliders and convert to HSV")
    parser.add_argument("--click", action="store_true",
                        help="Click a pixel in the video to set the colour")
    args = parser.parse_args()

    # ---------- Initialise colour selection ---------------------------------
    if args.click:
        lower_hsv = np.array([0, 0, 0], dtype=np.uint8)
        upper_hsv = np.array([0, 0, 0], dtype=np.uint8)
        click_selected = False
        current_frame = None

        def mouse_callback(event, x, y, flags, param):
            nonlocal lower_hsv, upper_hsv, click_selected, current_frame
            if event == cv2.EVENT_LBUTTONDOWN and current_frame is not None:
                bgr = current_frame[y, x]
                hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
                lower_hsv = np.maximum(hsv - np.array([10, 50, 50]), 0)
                upper_hsv = np.minimum(hsv + np.array([10, 255, 255]), np.array([179, 255, 255]))
                click_selected = True

        cv2.namedWindow("Webcam")
        cv2.setMouseCallback("Webcam", mouse_callback)

    elif args.rgb:
        rgb_initial = np.array([0, 0, 0], dtype=np.uint8)
        create_rgb_trackbars("RGB‑Tuner", rgb_initial)
        # will be overwritten each frame
        lower_hsv = np.array([0, 0, 0], dtype=np.uint8)
        upper_hsv = np.array([0, 0, 0], dtype=np.uint8)
    else:
        presets = load_color_presets()
        if args.color not in presets:
            raise ValueError(f"Colour '{args.color}' not recognised.")
        lower_hsv = presets[args.color]["lower"].copy()
        upper_hsv = presets[args.color]["upper"].copy()

    # ---------- Camera ------------------------------------------------------
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Unable to open webcam (device 0).")

    if args.tune:
        create_hsv_trackbars("HSV‑Tuner", lower_hsv, upper_hsv)

    print("Press ESC to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame capture failed – exiting.")
            break
        # store the latest frame for click mode
        if args.click:
            current_frame = frame

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Update HSV bounds according to mode
        if args.tune:
            lower_hsv, upper_hsv = read_hsv_from_trackbars("HSV‑Tuner")
        if args.rgb and not (click_selected if "click_selected" in locals() else False):
            rgb = read_rgb_from_trackbars("RGB‑Tuner")
            hsv_color = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
            lower_hsv = np.maximum(hsv_color - np.array([10, 50, 50]), 0)
            upper_hsv = np.minimum(hsv_color + np.array([10, 255, 255]), np.array([179, 255, 255]))
        if args.click and not click_selected:
            cv2.imshow("Webcam", frame)
            cv2.imshow("Mask", np.zeros_like(frame))
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue

        mask = get_mask(hsv, lower_hsv, upper_hsv)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            biggest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(biggest) > 500:
                (x, y), radius = cv2.minEnclosingCircle(biggest)
                center = (int(x), int(y))
                cv2.circle(frame, center, int(radius), (0, 255, 0), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                print(f"Object centre: ({center[0]}, {center[1]})")

        cv2.imshow("Webcam", frame)
        cv2.imshow("Mask", mask)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
