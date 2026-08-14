# src/main.py
import time
from color_tracker.tracker import DroneTracker
from motor import MotorController

def main():
    # Parameters
    BASELINE = 2.0  # feet
    FOCAL_LENGTH = 600.0
    TARGET_Z = 10.0  # Desired distance from cameras in feet
    TARGET_X = 0.0   # Desired center position

    try:
        # Initialize components
        tracker = DroneTracker(baseline=BASELINE, focal_length=FOCAL_LENGTH)
        motors = MotorController()
        
        print("System initialized. Tracking drones...")
        print("Press Ctrl+C to stop.")

        while True:
            # 1. Get positions from vision system
            positions = tracker.update()
            
            if positions is None:
                print("Failed to capture frames, retrying...")
                continue

            # 2. Process each drone (Yellow and Orange)
            for drone_id, pos in positions.items():
                if pos is not None:
                    x, y, z = pos
                    print(f"{drone_id.capitalize()} drone at X: {x:.2f}, Z: {z:.2f} ft")

                    # --- Simple Proportional Control Logic ---
                    # Adjust Z (Throttle/Pitch)
                    # If z > TARGET_Z, we need to move forward (increase pitch)
                    z_error = z - TARGET_Z
                    throttle = 50  # Hover base
                    pitch = z_error * 2.0  # Simple gain

                    # Adjust X (Roll)
                    # If x > TARGET_X, we need to move left
                    x_error = x - TARGET_X
                    roll = x_error * 2.0

                    # Clamp values (assuming -100 to 100 range)
                    pitch = max(min(pitch, 100), -100)
                    roll = max(min(roll, 100), -100)

                    # 3. Send commands to motors
                    motors.set_speeds(drone_id, throttle, 0, pitch, roll)
                else:
                    print(f"{drone_id.capitalize()} drone NOT detected.")

            time.sleep(0.1)  # Control loop frequency

    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'motors' in locals():
            motors.stop_all()
            motors.close()
        if 'tracker' in locals():
            tracker.release()

if __name__ == "__main__":
    main()
