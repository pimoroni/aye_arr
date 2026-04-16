from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote
from motor import Motor, pico_motor_shim
from pimoroni import REVERSED_DIR

# Create the remote and setup up what each of our buttons will do.
remote = PimoroniRemote()
receiver = NECRemoteReceiver(4, 1, 0)

# Create a list of motors
MOTOR_PINS = [pico_motor_shim.MOTOR_1, pico_motor_shim.MOTOR_2]
motors = [Motor(pins) for pins in MOTOR_PINS]

# Uncomment the below lines (and the top import) to
# reverse the driving direction of a motor
motors[0].direction(REVERSED_DIR)

SPEED = 0.5


def reverse():
    for m in motors:
        m.speed(-SPEED)


def forward():
    for m in motors:
        m.speed(SPEED)


def turn(d):
    if d > 0:
        motors[0].speed(SPEED)
        motors[1].speed(-SPEED)
    else:
        motors[1].speed(SPEED)
        motors[0].speed(-SPEED)


def arc(d):
    if d > 0:
        motors[0].speed(SPEED)
        motors[1].speed(SPEED / 2)
    else:
        motors[1].speed(SPEED)
        motors[0].speed(SPEED / 2)


def stop():
    for m in motors:
        m.stop()


remote.bind("UP", on_press=forward, on_release=stop)
remote.bind("DOWN", on_press=reverse, on_release=stop)
remote.bind("LEFT", on_press=(turn, -1), on_release=stop)
remote.bind("RIGHT", on_press=(turn, 1), on_release=stop)
remote.bind("ANTICLOCK", on_press=(arc, -1), on_release=stop)
remote.bind("CLOCKWISE", on_press=(arc, 1), on_release=stop)
receiver.bind(remote)


try:
    receiver.start()

    while True:
        receiver.decode()

finally:
    receiver.stop()
    for m in motors:
        m.disable()
