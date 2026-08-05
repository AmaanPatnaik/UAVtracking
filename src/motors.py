[object Object]import RPi.GPIO as GPIO
import time

class StepperL298N:
    """
    Handles low-level coil sequencing for a NEMA 17 bipolar stepper 
    connected to an L298N H-Bridge driver.
    """
    def __init__(self, pins):
        self.pins = pins
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
        # Full-step sequence for bipolar steppers
        self._sequence = [
            (1, 0, 1, 0), # Step 1
            (0, 1, 1, 0), # Step 2
            (0, 1, 0, 1), # Step 3
            (1, 0, 0, 1), # Step 4
        ]
        self._current_step = 0

    def step(self, direction=1, delay=0.01):
        """Move the motor one step."""
        self._current_step = (self._current_step + direction) % 4
        for pin, val in zip(self.pins, self._sequence[self._current_step]):
            GPIO.output(pin, val)
        time.sleep(delay)

    def rotate(self, steps, direction=1, speed=0.01):
        """Rotate the motor a specific number of steps."""
        for _ in range(abs(steps)):
            self.step(direction, delay=speed)

    def disable(self):
        """Turn off all coils to prevent overheating."""
        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)

class TurretHardware:
    """High-level manager for the Turret's three motors."""
    def __init__(self, config):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.azimuth = StepperL298N(tuple(config['gpio_pins']['azimuth']))
        self.pivot = StepperL298N(tuple(config['gpio_pins']['pivot']))
        self.spindex = StepperL298N(tuple(config['gpio_pins']['spindex']))

    def cleanup(self):
        """Safe shutdown of all GPIO."""
        self.azimuth.disable()
        self.pivot.disable()
        self.spindex.disable()
        GPIO.cleanup()
