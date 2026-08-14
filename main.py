import time
import cv2
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
        # Updated camera indices to 0 and 2 based on /dev/video* output
        tracker = DroneTracker(baseline=xBASELINE, focal_length=FOCAL_LENGTH, cam0_idx=0, cam1_idx=2)
        motors = MotorController()
        
        print(\"System initialized. Tracking drones...\")
        print(\"Press Ctrl+C to stop.\")

        while True:
            # 1. Get positions and frames from vision system
            positions, frame_l, frame_r = tracker.update()
            
            if positions is None:
                print(\"Failed to capture frames, retrying...\")
                continue

            # Display camera feeds
            cv2.imshow('Left Camera', frame_l)
            cv2.imshow('Right Camera', frame_r)
            cv2.waitKey(1)

            # 2. Process each drone (Yellow and Orange)
            for drone_id, pos in positions.items():
                if pos is not None:
                    x, y, z = pos
                    print(f\"{drone_id.capitalize()} drone at X: {x:.2f}, Z: {z:.2f} ft\")

                    # --- Simple Proportional Control Logic ---
                    # Adjust Z (Throttle/Pitch)
                    z_error = z - TARGET_Z
                    throttle = 50  # Hover base
                    pitch = z_error * 2.0  # Simple gain

                    # Adjust X (Roll)
                    x_error = x - TARGET_X
                    roll = x_error * 2.0

                    # Clamp values (assuming -100 to 100 range)
                    pitch = max(min(pitch, 100), -100)
                    roll = max(min(roll, 100), -100)

                    # 3. Send commands to motors
                    motors.set_speeds(drone_id, throttle, 0, pitch, roll)
                else:
                    print(f\"{drone_id.capitalize()} drone NOT detected.\")

            time.sleep(0.1)  # Control loop frequency

    except KeyboardInterrupt:
        print(\"Shutting down...\")
    except Exception as e:
        print(f\"Error: {e}\")
    finally:
        if 'motors' in locals():
            motors.stop_all()
            motors.close()
        if 'tracker' in locals():
            tracker.release()
        cv2.destroyAllWindows()

if __name__ == \"__main__\":
    main()"
