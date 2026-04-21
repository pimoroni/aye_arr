from motor import Motor, pico_motor_shim
from pimoroni import REVERSED_DIR

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
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


# Function for driving forward or backward
def forward(d):
    if d > 0:
        left.speed(speed)
        right.speed(speed)
    else:
        left.speed(-speed)
        right.speed(-speed)


# Function for turning on the spot
def turn(d):
    if d > 0:
        left.speed(speed)
        right.speed(-speed)
    else:
        left.speed(-speed)
        right.speed(speed)


# Function for turning in an arc
def arc(d):
    if d > 0:
        left.speed(speed)
        right.speed(speed / 2)
    else:
        left.speed(speed / 2)
        right.speed(speed)


# Function to stop moving
def stop():
    left.stop()
    right.stop()


# Function for updating the motor speed for future motions
def update_speed(value):
    global speed
    speed = value


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("UP", on_press=(forward, 1), on_release=stop)
remote.bind("DOWN", on_press=(forward, -1), on_release=stop)
remote.bind("LEFT", on_press=(turn, -1), on_release=stop)
remote.bind("RIGHT", on_press=(turn, 1), on_release=stop)
remote.bind("ANTICLOCK", on_press=(arc, -1), on_release=stop)
remote.bind("CLOCKWISE", on_press=(arc, 1), on_release=stop)
remote.bind("1_RED", (update_speed, 0.2))
remote.bind("2_GREEN", (update_speed, 0.3))
remote.bind("3_BLUE", (update_speed, 0.4))
remote.bind("4_CYAN", (update_speed, 0.5))
remote.bind("5_MAGENTA", (update_speed, 0.6))
remote.bind("6_YELLOW", (update_speed, 0.7))
remote.bind("7_WARM", (update_speed, 0.8))
remote.bind("8_WHITE", (update_speed, 0.9))
remote.bind("9_COOL", (update_speed, 1.0))

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0)
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
