from typing import Tuple

class PIDController:
    """Standard PID implementation for smooth motor tracking."""
    def __init__(self, config: dict):
        self.kp = config['pid']['kp']
        self.ki = config['pid']['ki']
        self.kd = config['pid']['kd']
        self.integral = 0
        self.last_error = 0

    def calculate(self, error: float) -> float:
        self.integral += error
        derivative = error - self.last_error
        self.last_error = error
        return (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

class TurretKinematics:
    """Maps pixel errors to motor commands using PID."""
    def __init__(self, config: dict):
        self.config = config
        self.pid_h = PIDController(config)
        self.pid_v = PIDController(config)

    def get_motor_commands(self, target_pos: Tuple[int, int], center_pos: Tuple[int, int]) -> Tuple[int, float, int, float]:
        """
        Calculates direction and speed for Azimuth and Pivot motors.
        Returns: (dir_h, speed_h, dir_v, speed_v)
        """
        err_x = target_pos[0] - center_pos[0]
        err_y = target_pos[1] - center_pos[1]

        output_h = self.pid_h.calculate(err_x)
        output_v = self.pid_v.calculate(err_y)

        return (
            1 if output_h > 0 else -1,
            self._clamp_speed(abs(output_h)),
            1 if output_v > 0 else -1,
            self._clamp_speed(abs(output_v))
        )

    def _clamp_speed(self, val: float) -> float:
        """Maps PID output to a delay value between max and min speed."""
        max_d = self.config['pid']['max_speed_delay']
        min_d = self.config['pid']['min_speed_delay']
        # Inverse relationship: higher PID output = lower delay = faster speed
        return max(max_d, min(min_d, 0.01 / (val + 1)))
