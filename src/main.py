import json
import threading
import time
import os
from fastapi import FastAPI
import uvicorn

from motors import TurretHardware
from vision import DroneDetector
from kinematics import TurretKinematics

# Load Config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'turret_config.json')
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

app = FastAPI()
system_state = {"running": False, "target_locked": False, "shots_fired": 0}

# Global hardware objects
hw = TurretHardware(CONFIG)
vision = DroneDetector(CONFIG)
kinematics = TurretKinematics(CONFIG)

def perform_startup_test():
    """Moves each motor slightly on boot to verify hardware and checks for camera."""
    print("\n--- Starting Hardware Self-Test ---")
    
    # 1. CAMERA CHECK
    print("Checking camera...")
    if not vision.cap.isOpened():
        print("CRITICAL ERROR: Camera not detected!")
        print("Entering Panic Mode: Spinning all motors continuously...")
        try:
            while True:
                # Spin all motors continuously as a warning
                hw.azimuth.step(direction=1, delay=0.002)
                hw.pivot.step(direction=1, delay=0.002)
                hw.spindex.step(direction=1, delay=0.002)
        except KeyboardInterrupt:
            print("Panic mode stopped by user.")
            return

    try:
        # Test Azimuth
        print("Testing Azimuth...")
        hw.azimuth.rotate(100, direction=1, speed=0.005)
        time.sleep(0.2)
        hw.azimuth.rotate(100, direction=-1, speed=0.005)

        # Test Pivot
        print("Testing Pivot...")
        hw.pivot.rotate(100, direction=1, speed=0.005)
        time.sleep(0.2)
        hw.pivot.rotate(100, direction=-1, speed=0.005)

        # Test Spindexer (Move one slot)
        print("Testing Spindexer...")
        hw.spindex.rotate(CONFIG['mechanical']['spindexer_steps_per_shot'], direction=1, speed=0.005)
        
        print("--- Hardware Self-Test Complete! ---\n")
    except Exception as e:
        print(f"Startup test failed: {e}")

def turret_loop():
    """The main control loop for tracking and firing."""
    global system_state
    center = (CONFIG['vision']['camera_width'] // 2, CONFIG['vision']['camera_height'] // 2)
    lock_start_time = None

    print("Turret Brain initialized and waiting for start command...")

    try:
        while True:
            if not system_state["running"]:
                time.sleep(0.1)
                continue

            # 1. Target Detection (Default to red)
            target, frame = vision.get_target("red")
            
            if target:
                # 2. Tracking: Convert pixel error to motor movements
                dir_h, speed_h, dir_v, speed_v = kinematics.get_motor_commands(target, center)
                
                # Execute movements synchronously to reduce jitter
                hw.step_synchronized([
                    (hw.azimuth, dir_h, speed_h),
                    (hw.pivot, dir_v, speed_v)
                ])

                # 3. Lock-on Check
                dist_from_center = ((target[0] - center[0])**2 + (target[1] - center[1])**2)**0.5
                if dist_from_center < CONFIG['vision']['lock_zone_pixels']:
                    if lock_start_time is None:
                        lock_start_time = time.time()
                    
                    if time.time() - lock_start_time > CONFIG['vision']['lock_duration_seconds']:
                        print(f"TARGET LOCKED! Firing ball {system_state['shots_fired'] + 1}...")
                        hw.spindex.rotate(CONFIG['mechanical']['spindexer_steps_per_shot'])
                        system_state["shots_fired"] += 1
                        lock_start_time = None
                else:
                    lock_start_time = None
            else:
                lock_start_time = None

    except Exception as e:
        print(f"Critical error in turret loop: {e}")
    finally:
        hw.cleanup()

@app.get("/start")
def start():
    system_state["running"] = True
    return {"status": "Turret Active"}

@app.get("/stop")
def stop():
    system_state["running"] = False
    return {"status": "Turret Stopped"}

@app.get("/status")
def status():
    return system_state

@app.get("/reset")
def reset():
    system_state["shots_fired"] = 0
    return {"status": "Stats Reset"}

if __name__ == "__main__":
    perform_startup_test()
    t = threading.Thread(target=turret_loop, daemon=True)
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)