from motor import Motor, pico_motor_shim
from pimoroni import REVERSED_DIR

import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Control a 2-wheeled robot built using a Raspberry Pi Pico and
Pimoroni Motor Shim for Pico using the Pimoroni Aye Arr Remote.
This version lets the driving speed be adjusted using the number buttons.

Actions:
- UP Button [Press + Hold] = Drive Forward
- DOWN Button [Press + Hold] = Drive Backward
- LEFT Button [Press + Hold] = Turn Left
- RIGHT Button [Press + Hold] = Turn Right
- ANTICLOCK Button [Press + Hold] = Arc Forward-Left
- CLOCKWISE Button [Press + Hold] = Arc Forward-Right
- Directional Buttons [Release] = Stop Driving
- (0)-(9) Buttons [Press] = Set Next Speed

An IR receiver should be connected to the IR_RX_PIN of your board.
E.g. an IR Stick connected to the 3V, GND, and SDA of the Motor Shim's Qw/ST port.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 4           # The pin to listen for IR pulses on
STARTING_SPEED = 0.5    # The speed the motors will drive at initially

# Variables
speed = STARTING_SPEED

# Set up the left and right motors
left = Motor(pico_motor_shim.MOTOR_1)
right = Motor(pico_motor_shim.MOTOR_2)

# Reverse the driving direction of the left motor
# to make the movement code more understandable
left.direction(REVERSED_DIR)


# Drive forward or backward
def forward(d):
    if d > 0:
        left.speed(speed)
        right.speed(speed)
        print(f"Driving Forward at {int(speed*100)}%")
    else:
        left.speed(-speed)
        right.speed(-speed)
        print(f"Driving Backward at {int(speed*100)}%")


# Turn on the spot
def turn(d):
    if d > 0:
        left.speed(speed)
        right.speed(-speed)
        print(f"Turning Right at {int(speed*100)}%")
    else:
        left.speed(-speed)
        right.speed(speed)
        print(f"Turning Left at {int(speed*100)}%")


# Turn in a forward arc
def arc(d):
    if d > 0:
        left.speed(speed)
        right.speed(speed / 2)
        print(f"Arcing Forward-Right at {int(speed*100)}%")
    else:
        left.speed(speed / 2)
        right.speed(speed)
        print(f"Arcing Forward-Left at {int(speed*100)}%")


# Stop moving
def stop():
    left.stop()
    right.stop()
    print("Stopping")


# Update the motor speed for future motions
def update_speed(value):
    global speed
    speed = value
    print(f"Speed updated to {int(speed*100)}%")


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("UP", on_press=(forward, 1), on_release=stop)
remote.bind("DOWN", on_press=(forward, -1), on_release=stop)
remote.bind("LEFT", on_press=(turn, -1), on_release=stop)
remote.bind("RIGHT", on_press=(turn, 1), on_release=stop)
remote.bind("ANTICLOCK", on_press=(arc, -1), on_release=stop)
remote.bind("CLOCKWISE", on_press=(arc, 1), on_release=stop)
remote.bind("1_RED", (update_speed, 0.1), on_repeat=None)
remote.bind("2_GREEN", (update_speed, 0.2), on_repeat=None)
remote.bind("3_BLUE", (update_speed, 0.3), on_repeat=None)
remote.bind("4_CYAN", (update_speed, 0.4), on_repeat=None)
remote.bind("5_MAGENTA", (update_speed, 0.5), on_repeat=None)
remote.bind("6_YELLOW", (update_speed, 0.6), on_repeat=None)
remote.bind("7_WARM", (update_speed, 0.7), on_repeat=None)
remote.bind("8_WHITE", (update_speed, 0.8), on_repeat=None)
remote.bind("9_COOL", (update_speed, 0.9), on_repeat=None)
remote.bind("0_RAINBOW", (update_speed, 1.0), on_repeat=None)

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_NONE)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid feeling sluggish
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
    left.disable()
    right.disable()
