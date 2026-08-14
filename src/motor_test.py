import RPi.GPIO as GPIO
import time

# =========================================================
# HARDCODED PIN CONFIGURATION (Directly from your diagram)
# =========================================================
MOTORS = {
    "AZIMUTH": {"STEP": 17, "DIR": 27, "ENABLE": 22},
    "PIVOT":   {"STEP": 5,  "DIR": 6,  "ENABLE": 13},
    "FIRE":    {"STEP": 12, "DIR": 16, "ENABLE": 20},
}

def setup_motors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for name, pins in MOTORS.items():
        print(f"Configuring {name}: STEP={pins['STEP']}, DIR={pins['DIR']}, EN={pins['ENABLE']}")
        GPIO.setup(pins['STEP'], GPIO.OUT)
        GPIO.setup(pins['DIR'], GPIO.OUT)
        GPIO.setup(pins['ENABLE'], GPIO.OUT)
        
        # Set Direction to Clockwise
        GPIO.output(pins['DIR'], GPIO.HIGH)
        
        # Corrected: HIGH = ENABLED based on user feedback
        GPIO.output(pins['ENABLE'], GPIO.HIGH)
        print(f"  -> {name} ENABLED (Pin {pins['ENABLE']} set to HIGH)")

def run_full_blast():
    print("\n!!! WARNING: MOTORS RUNNING AT FULL BLAST !!!")
    print("Press Ctrl+C to stop immediately.\n")
    
    try:
        while True:
            # High-speed pulse generation
            for name, pins in MOTORS.items():
                GPIO.output(pins['STEP'], GPIO.HIGH)
            
            time.sleep(0.001) 
            
            for name, pins in MOTORS.items():
                GPIO.output(pins['STEP'], GPIO.LOW)
                
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\nStopping motors...")
    finally:
        # Corrected: LOW = DISABLED to prevent overheating
        for name, pins in MOTORS.items():
            GPIO.output(pins['ENABLE'], GPIO.LOW)
        GPIO.cleanup()
        print("GPIO Cleaned up. Exit.")

if __name__ == "__main__":
    try:
        setup_motors()
        run_full_blast()
    except Exception as e:
        print(f"Error: {e}")
        GPIO.cleanup()