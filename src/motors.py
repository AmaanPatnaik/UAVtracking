import RPi.GPIO as GPIO
import time

class StepperA4988:
    """
    Handles step/dir control for a NEMA 17 bipolar stepper 
    connected to an A4988 driver.
    """
    def __init__(self, step_pin, dir_pin, enable_pin=None):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        
        # Setup Pins
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        if self.enable_pin is not None:
            GPIO.setup(self.enable_pin, GPIO.OUT)
            self.disable() # Start disabled

    def step(self, direction=1, delay=0.005):
        """
        Move the motor one step.
        direction: 1 for CW, 0 for CCW
        delay: Time between pulses (seconds). Smaller = Faster.
        """
        GPIO.output(self.dir_pin, GPIO.HIGH if direction == 1 else GPIO.LOW)
        
        # Create a pulse on the STEP pin
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(self.step_pin, GPIO.LOW)
        time.sleep(delay)

    def rotate(self, steps, direction=1, speed=0.005):
        """Rotate the motor a specific number of steps."""
        self.enable()
        for _ in range(abs(steps)):
            self.step(direction, speed)

    def enable(self):
        """Energize coils to hold position."""
        if self.enable_pin is not None:
            GPIO.output(self.enable_pin, GPIO.LOW)

    def disable(self):
        """De-energize coils to save power and prevent heat."""
        if self.enable_pin is not None:
            GPIO.output(self.enable_pin, GPIO.HIGH)

class TurretHardware:
    """High-level manager for the Turret's three A4988 motors."""
    def __init__(self, config):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Helper to extract pins from config dictionary
        def get_motor(key):
            pins = config['gpio_pins'][key]
            return StepperA4988(pins['step'], pins['dir'], pins['enable'])

        self.azimuth = get_motor('azimuth')
        self.pivot = get_motor('pivot')
        self.spindex = get_motor('spindex')

    def cleanup(self):
        """Safe shutdown of all GPIO."""
        self.azimuth.disable()
        self.pivot.disable()
        self.spindex.disable()
        GPIO.cleanup()