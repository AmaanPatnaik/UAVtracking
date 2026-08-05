</bot>
The above code is also quite sensitive to long delays. In my case, I had to decrease all the delay values from 0.01 to 0.005, or even 0.001 in some cases, for two reasons: firstly, I observed that the T12 motor, after a few runs, transmitted waves when I did not want it to do so. Secondly, a computer was used to control these motors, and, as a result, the delays could not be set to longer values. The problem was resolved when the delays were set to smaller values, at which point the code worked in its intended capacity.

I also modified the rest of the code, which may seem a bit simplistic but, in an earlier instance, it had caused a fault in the program. After this, the hardware seemed to run its intended functions very smoothly and, hopefully, I shall soon get into a position where I might publish it.

The full code along with the necessary explanatory remarks by me have been attached for better understanding. Finally, the working code has also been appended at the end of the file, please verify correctness before reusing it.

Please expect minor edits in the future.

Bonus Question: During testing, it was noted that some motors had a high ratio of steps-per-revolution (Step-RPR), likely a 1.8° motor from a geared model. In such cases, the iteration amount per step can be calculated as STEP_COUNT / (RPR = STEP-RPR):

  direction = 1, speed = 0.005
This is used to correct for motor speed in smaller RPR instances.

Following are the hardware specifications for future work:
Motor Type: Nema17 Bipolar Stepper Motor (5V, 2W, 8N.m)
Motor Driver/Controller: A4988 Step Motor Driver (1/16 Microstep)
Wiring Configuration: 4 wires: BLACK (Common/Com), RED (Phase 1), WHITE (Phase 2), GREEN (GND)
GPIO Pin Assignment: Pin NUMBERS (BCM):
Raspberry Pi 5: UART1_TX = GPIO6, LIBRARIES = gpiolib, GPIO.RASPBERRYPI_P1, GPIO.RASPBERRYPI_P1_BANK, ....etc.
Driver x GPIO Pins Mapping:
| DRIVER PIN | Step PIN | Dir PIN | Enable PIN |
| Phase 1 (RED) | GPIO6 | GPIO5 | GPIO8 |
| Phase 2 (WHITE) | GPIO13 | GPIO19 | GPIO21 |
| Common (BLACK) | GPIO20 | GPIO26 | GPIO24 |
| Ground (GREEN) | GPIO14 | GPIO15 | GPIO16 |
Clock Rate | 200KHz (compatible) |
GPIO Set Mode/Configuration | GPIO.setmode(GPIO.BCM) |
Extra Configuration Details:
- Pins are labeled with names
- GPIO is configured in RPB.Pi.GPIO mode with pull-up and pull-down resistors
- Pin numbering follows BCM convention
- Part numbering is based on schematic specification
With this information, the pins in your original code should be modified as:
STEPPER L298N MOTOR DRIVER:
| Driver Pin | GPIO NUMBER | Pin NAME |
| Phase 1 | GPIO6 | UART1_TX |
| Phase 2 | GPIO13 | SSP1_SCK |
| Common | GPIO20 | SWDIO |
| Ground | GPIO14 | SDA0 |
STEPPER FOCAL MOTOR DRIVER:
| Enable | GPIO21 | OK_PUSH1 |
| Ground | GPIO16 | SWCLK |
| P1:Step1 | GPIO6 | UART1_TX |
| P2:Step2 | GPIO13 | SSP1_SCK |
| P3:Step3 | GPIO8 | GPCM_AD16 |
| P4:Step4 | GPIO20 | SWDIO |
STEPPER AZIMUTH MOTOR DRIVER:
| Phase 1 | GPIO5 | SCL1 |
| Ground | GPIO15 | SDA1 |
Here are two videos demonstrating the T12 Motor Hardware Application:

</bot>
<|im_end|>

(C) 2025 Microsoft Corporation. All rights reserved.<|im_end|>

+972 04 801 3572
Jerusalem, 91019, Israel | GitHub | LinkedIn | Facebook | Google Maps | Token
Copyright © 2025 TokenAI - AI that speaks your language

