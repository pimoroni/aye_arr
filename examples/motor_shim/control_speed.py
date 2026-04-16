from motor import Motor, pico_motor_shim
from pimoroni import REVERSED_DIR

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

# Create the remote and setup up what each of our buttons will do.
remote = PimoroniRemote()
receiver = NECRemoteReceiver(4, 1, 0)

# Create a list of motors
MOTOR_PINS = [pico_motor_shim.MOTOR_1, pico_motor_shim.MOTOR_2]
motors = [Motor(pins) for pins in MOTOR_PINS]

# Uncomment the below lines (and the top import) to
# reverse the driving direction of a motor
motors[0].direction(REVERSED_DIR)

motor_speed = 0.5


def update_speed(value):
    global motor_speed
    motor_speed = value


def reverse():
    for m in motors:
        m.speed(-motor_speed)


def forward():
    for m in motors:
        m.speed(motor_speed)


def turn(d):
    if d > 0:
        motors[0].speed(motor_speed)
        motors[1].speed(-motor_speed)
    else:
        motors[1].speed(motor_speed)
        motors[0].speed(-motor_speed)


def arc(d):
    if d > 0:
        motors[0].speed(motor_speed)
        motors[1].speed(motor_speed / 2)
    else:
        motors[1].speed(motor_speed)
        motors[0].speed(motor_speed / 2)


def stop():
    for m in motors:
        m.stop()


remote.bind("UP", on_press=forward, on_release=stop)
remote.bind("DOWN", on_press=reverse, on_release=stop)
remote.bind("LEFT", on_press=(turn, -1), on_release=stop)
remote.bind("RIGHT", on_press=(turn, 1), on_release=stop)
remote.bind("ANTICLOCK", on_press=(arc, -1), on_release=stop)
remote.bind("CLOCKWISE", on_press=(arc, 1), on_release=stop)
remote.bind("1_RED", (update_speed, 0.2))
remote.bind("4_CYAN", (update_speed, 0.5))
remote.bind("2_GREEN", (update_speed, 0.3))
remote.bind("5_MAGENTA", (update_speed, 0.6))
remote.bind("3_BLUE", (update_speed, 0.4))
remote.bind("6_YELLOW", (update_speed, 0.7))
remote.bind("7_WARM", (update_speed, 0.8))
remote.bind("8_WHITE", (update_speed, 0.9))
remote.bind("9_COOL", (update_speed, 1.0))
receiver.bind(remote)


try:
    receiver.start()

    while True:
        receiver.decode()

finally:
    receiver.stop()
    for m in motors:
        m.disable()
