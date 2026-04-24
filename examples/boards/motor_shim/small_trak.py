import time

from motor import Motor, pico_motor_shim
from pimoroni import REVERSED_DIR

from machine import Pin
from collections import namedtuple

from aye_arr.logging import LOG_NONE
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Program a sequence of movements using the Pimoroni Aye Arr Remote for a 2-wheeled
robot built using a Raspberry Pi Pico and Pimoroni Motor Shim for Pico to perform.

Actions:
- RECORD Button [Press] = Start / Stop Recording
- PLAY_PAUSE [Press] = Play / Pause Playback
- In Recording Mode:
    - UP, DOWN, LEFT, RIGHT, OK_STOP Buttons [Press] = Select the direction to program
    - (1)-(9) Buttons [Press] = Add digit to number of steps of the direction
    - RETURN_UNDO Button [Press] = Undo the last digit or direction

An IR receiver should be connected to the IR_RX_PIN of your board.
E.g. an IR Stick connected to the 3V, GND, and SDA of the Motor Shim's Qw/ST port.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 4           # The pin to listen for IR pulses on
SPEED = 0.5             # The speed the motors will drive at
CYCLE_DURATION = 1      # The time each cycle takes

# Tuple for storing recorded the name and cycles of an action
Action = namedtuple("Action", ("name", "cycles"))

# Variables
sequence = []           # The list containing the actions recorded

# Set up the left and right motors
left = Motor(pico_motor_shim.MOTOR_1)
right = Motor(pico_motor_shim.MOTOR_2)

# Reverse the driving direction of the left motor
# to make the movement code more understandable
left.direction(REVERSED_DIR)

# Set up the Pico's LED to show our record/playback state
led = Pin("LED", Pin.OUT)
led.off()


# Function for driving forward
def drive_forward():
    left.speed(SPEED)
    right.speed(SPEED)
    print("Driving Forward")


# Function for turning left
def turn_left():
    left.speed(-SPEED)
    right.speed(SPEED)
    print("Turning Left")


# Function for turning right
def turn_right():
    left.speed(SPEED)
    right.speed(-SPEED)
    print("Turning Right")


# Function for driving backward
def drive_backward():
    left.speed(-SPEED)
    right.speed(-SPEED)
    print("Driving Backward")


# Function for stopping
def stop():
    left.stop()
    right.stop()
    print("Stopping")


# Mapping from useful names to functions
ACTIONS = {
    "FORWARD": drive_forward,
    "LEFT": turn_left,
    "RIGHT": turn_right,
    "BACKWARD": drive_backward,
    "STOP": stop
}


# Base State Class
class State:
    def update(self):
        pass

    def end(self):
        pass

    def on_action(self, _):
        pass

    def on_command(self, _):
        return False

    def on_record(self):
        pass

    def on_undo(self):
        pass

    def on_play(self):
        pass


# Record State for capturing actions
class RecordState(State):
    FLASHING_INTERVAL_MS = 100

    def __init__(self):
        global sequence
        self.__action = None
        self.__number = None
        self.__last = time.ticks_ms()
        self.__line_finished = True
        sequence = []
        print("--- Recording Sequence ---")

    def update(self):
        global led
        now = time.ticks_ms()
        if time.ticks_diff(now, self.__last) >= self.FLASHING_INTERVAL_MS:
            led.toggle()
            self.__last = now
        return None

    def end(self):
        global led, sequence
        led.off()

        if not self.__line_finished:
            print()
            self.__line_finished = True

        if len(sequence) > 0:
            print("--- Sequence Recorded ---")
            for action in sequence:
                print(f" * {action.name} for {action.cycles} cycles")
            print("--- Ready For Playback ---")
        else:
            print("--- No Actions Recorded ---")

    def on_action(self, action):
        print(f" + {action} for: ", end="")
        self.__line_finished = False
        self.__action = action
        self.__number = ""

    def on_command(self, cmd):
        global sequence
        try:
            num = remote.NUMBERS[cmd]
        except KeyError:
            if self.__action is not None and cmd != "RETURN_UNDO" and len(self.__number) > 0:
                sequence.append(Action(self.__action, int(self.__number)))
                print(" cycles")
                self.__line_finished = True
                self.__action = None
                self.__number = ""
            return False

        print(str(num), end="")
        self.__line_finished = False
        self.__number += str(num)
        return True

    def on_record(self):
        return IdleState

    def on_undo(self):
        if not self.__line_finished:
            print()
            self.__line_finished = True

        if self.__action is not None:
            if len(self.__number) > 0:
                self.__number = self.__number[:-1]
                print(" - Undoing number")
            else:
                self.__action = None
                print(" - Undoing action")
        elif len(sequence) > 0:
            sequence.pop()
            print(" - Undoing last action")
        else:
            print(" - Nothing to undo")

    def on_play(self):
        if len(sequence) > 0:
            return PlayState
        return None


# Play State for playing back recorded actions
class PlayState(State):
    def __init__(self):
        self.__index = 0
        self.__play_action()
        led.on()

    def update(self):
        self.__index += 1
        if self.__index >= len(sequence):
            return IdleState

        self.__play_action()
        return None

    def end(self):
        led.off()

    def __play_action(self):
        active_action = sequence[self.__index]
        for i in range(active_action.cycles):
            print(f"[{i + 1}/{active_action.cycles}] ", end="")
            ACTIONS[active_action.name]()
            time.sleep(CYCLE_DURATION)

    def on_play(self):
        return IdleState


# Idle State for when the robot is not recording or playing back
class IdleState(State):
    def __init__(self):
        stop()

    def on_record(self):
        return RecordState

    def on_play(self):
        if len(sequence) > 0:
            return PlayState
        return None


# Set the initial state to be recording
state = RecordState()


# Pass an action through to the current state
def on_action(action_name):
    state.on_action(action_name)


# Pass a command through to the current state
def on_command(cmd):
    return state.on_command(cmd)


# Call a function on the current state, and switch to any new state that is returned
def on_function(func):
    global state
    new = eval("state." + func)()   # Spicy way to call the named function on the current state
    if new is not None:
        state.end()     # End the current state
        state = new()   # Start the new state by calling its initialiser


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.on_known = on_command
remote.bind("UP", (on_action, "FORWARD"), on_repeat=None)
remote.bind("DOWN", (on_action, "BACKWARD"), on_repeat=None)
remote.bind("LEFT", (on_action, "LEFT"), on_repeat=None)
remote.bind("RIGHT", (on_action, "RIGHT"), on_repeat=None)
remote.bind("OK_STOP", (on_action, "STOP"), on_repeat=None)
remote.bind("RECORD", (on_function, "on_record"), on_repeat=None)
remote.bind("RETURN_UNDO", (on_function, "on_undo"), on_repeat=None)
remote.bind("PLAY_PAUSE", (on_function, "on_play"), on_repeat=None)

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0, logging_level=LOG_NONE)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()

    # Loop until the effect stops or the "Boot" button is pressed
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid inputs feeling sluggish
        receiver.decode()

        # Update the current state, and check for state changes
        new = state.update()
        if new is not None:
            state.end()     # End the current state
            state = new()   # Start the new state by calling its initialiser

# Stop any running effects and turn off all the outputs
finally:
    receiver.stop()
