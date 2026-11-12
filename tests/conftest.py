"""
Stubs that let the MicroPython library import and run under CPython.

`machine` and `rp2` are replaced with fakes that record what the library asks of
them, so the protocol layers can be exercised without an RP board. `const` and
`micropython` are names the MicroPython compiler resolves without an import, so
they are placed in builtins.

MicroPython does not mangle private names, which this library relies on for
`__analyse` and the callback methods to override across the class hierarchy.
CPython does mangle, so a test that needs one of those reaches it through its
mangled name and says so.
"""

import builtins
import sys
import time
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class FakePin:
    """A machine.Pin that records its output state.

    The rp2 port returns the same object for a given GPIO, which the library
    depends on when it compares a PIO's base against a pin, so instances are
    cached per number here too.
    """

    IN = 0
    OUT = 1
    PULL_UP = 2
    PULL_DOWN = 3

    __instances = {}

    def __new__(cls, pin_num, *args):
        if pin_num not in cls.__instances:
            instance = super().__new__(cls)
            instance.pin_num = pin_num
            instance.state = 0
            cls.__instances[pin_num] = instance
        return cls.__instances[pin_num]

    def on(self):
        self.state = 1

    def off(self):
        self.state = 0

    def __repr__(self):
        return f"FakePin({self.pin_num})"


class FakeMem32:
    """The mem32 register window, reading back every bit set.

    `wait_for_send` polls a TX flag until it reads high, so an all-ones read
    keeps it from blocking.
    """

    def __init__(self):
        self.writes = []

    def __getitem__(self, address):
        return 0xffffffff

    def __setitem__(self, address, value):
        self.writes.append((address, value))


class FakeStateMachine:
    """A StateMachine that records the words put to its TX FIFO."""

    def __init__(self, index, program, **kwargs):
        self.index = index
        self.program = program
        self.kwargs = kwargs
        self.puts = []
        self.__active = 0
        self.__handler = None
        self.__rx = []

    def active(self, value=None):
        if value is None:
            return self.__active
        self.__active = value
        return self.__active

    def put(self, value):
        self.puts.append(value)

    def irq(self, handler):
        self.__handler = handler

    def rx_fifo(self):
        return len(self.__rx)

    def get(self):
        return self.__rx.pop(0)

    def rx_address(self):
        """The address of this state machine's RX FIFO register, as the RP2 maps it."""
        return 0x50200020 + (self.index // 4) * 0x100000 + (self.index % 4) * 4

    def feed(self, *count_pairs):
        """
        Queue count pairs as though the PIO program had received them, where a running
        DMA channel copies them off at once, as the hardware would.
        """
        for count_pair in count_pairs:
            for channel in FakeDMA.channels:
                if channel.running and channel.read == self.rx_address():
                    channel.transfer(count_pair)
                    break
            else:
                self.__rx.append(count_pair)

    def trigger_irq(self):
        """Run the handler the receiver registered, as the PIO's interrupt would."""
        if self.__handler is not None:
            self.__handler(self)


class FakeMemory:
    """
    Addresses for the buffers uctypes.addressof is asked about, each 4 bytes past a 64KB
    boundary, so code aligning a ring within a buffer has to move it along.
    """

    __buffers = []

    @classmethod
    def addressof(cls, buffer):
        for base, held in cls.__buffers:
            if held is buffer:
                return base
        base = 0x20000004 + len(cls.__buffers) * 0x10000
        cls.__buffers.append((base, buffer))
        return base

    @classmethod
    def find(cls, address):
        """The buffer an address falls in, and that buffer's own address."""
        for base, buffer in cls.__buffers:
            if base <= address < base + len(buffer):
                return buffer, base
        raise ValueError(f"no buffer at 0x{address:08x}")

    @classmethod
    def reset_all(cls):
        cls.__buffers.clear()


class FakeDMA:
    """
    An rp2.DMA channel that copies each count a state machine is fed into the buffer it
    writes to, wrapping in its ring and counting down, as a channel paced by the RX FIFO does.
    Channels can be refused, as the hardware's run out.
    """

    channels = []
    refuse = False

    def __init__(self):
        if FakeDMA.refuse:
            raise OSError("no free DMA channel")
        self.read = None
        self.write = None
        self.count = 0
        self.ctrl = None
        self.running = False
        self.closed = False
        self.__next = None
        FakeDMA.channels.append(self)

    def pack_ctrl(self, **fields):
        return dict(fields)

    def config(self, read=None, write=None, count=None, ctrl=None, trigger=False):
        self.read, self.write, self.count, self.ctrl = read, write, count, ctrl
        self.__next = write
        self.running = trigger

    def active(self, value=None):
        if value is None:
            return self.running
        self.running = bool(value)
        return self.running

    def close(self):
        self.running = False
        self.closed = True
        FakeDMA.channels.remove(self)

    def transfer(self, word):
        """Write one word where the channel points, then step on round its ring."""
        buffer, base = FakeMemory.find(self.__next)
        offset = self.__next - base
        buffer[offset:offset + 4] = word.to_bytes(4, "little")

        ring = 1 << self.ctrl["ring_size"]
        start = self.__next & ~(ring - 1)
        self.__next = start + (self.__next - start + 4) % ring
        self.count -= 1
        if self.count == 0:
            self.running = False

    @classmethod
    def reset_all(cls):
        cls.channels.clear()
        cls.refuse = False


class FakePIO:
    """A PIO instance tracking the GPIO base it was given.

    Construction raises ValueError beyond the RP2350's three PIOs, matching the
    check the library makes.
    """

    SHIFT_LEFT = 0
    SHIFT_RIGHT = 1
    JOIN_RX = 1
    JOIN_TX = 2
    JOIN_NONE = 0
    OUT_LOW = 0
    OUT_HIGH = 1
    IN_LOW = 2

    __instances = {}

    def __new__(cls, index):
        if index < 0 or index > 2:
            raise ValueError("pio out of range")
        if index not in cls.__instances:
            instance = super().__new__(cls)
            instance.index = index
            instance.base_sets = []
            instance.base = FakePin(0)
            cls.__instances[index] = instance
        return cls.__instances[index]

    def gpio_base(self, base=None):
        if base is None:
            return self.base
        self.base = FakePin(base)
        self.base_sets.append(base)
        return None

    @classmethod
    def reset_all(cls):
        cls.__instances.clear()


class FakeTicks:
    """MicroPython's wrapping millisecond counter, under a test's control.

    The period matches the 2**30 most ports use, so `ticks_diff` wraps where the
    library would see it wrap.
    """

    PERIOD = 1 << 30

    def __init__(self):
        self.now = 0

    def ms(self):
        return self.now % self.PERIOD

    def advance(self, milliseconds):
        self.now += milliseconds
        return self.ms()

    def diff(self, ticks1, ticks2):
        difference = (ticks1 - ticks2) & (self.PERIOD - 1)
        if difference >= self.PERIOD // 2:
            return difference - self.PERIOD
        return difference

    def add(self, ticks, delta):
        return (ticks + delta) % self.PERIOD


ticks = FakeTicks()


def __install_stubs():
    """Place the MicroPython-only modules and names where an import finds them."""

    builtins.const = lambda value: value

    # The library reads the tick functions off the standard time module
    time.ticks_ms = ticks.ms
    time.ticks_diff = ticks.diff
    time.ticks_add = ticks.add

    micropython = types.ModuleType("micropython")
    micropython.const = lambda value: value
    micropython.native = lambda func: func
    micropython.viper = lambda func: func
    builtins.micropython = micropython
    sys.modules["micropython"] = micropython

    machine = types.ModuleType("machine")
    machine.Pin = FakePin
    machine.mem32 = FakeMem32()
    sys.modules["machine"] = machine

    rp2 = types.ModuleType("rp2")
    rp2.PIO = FakePIO
    rp2.StateMachine = FakeStateMachine
    rp2.DMA = FakeDMA

    uctypes = types.ModuleType("uctypes")
    uctypes.addressof = FakeMemory.addressof
    sys.modules["uctypes"] = uctypes

    # The PIO programs are only defined, never run, so the decorator can pass
    # the function through and leave its assembly names unresolved
    rp2.asm_pio = lambda **kwargs: (lambda func: func)
    sys.modules["rp2"] = rp2


__install_stubs()


@pytest.fixture(autouse=True)
def reset_pio_state():
    """Clear the PIO instances between tests so base tracking starts fresh."""
    FakePIO.reset_all()
    yield
    FakePIO.reset_all()


@pytest.fixture(autouse=True)
def reset_dma_state():
    """Free every DMA channel and buffer address between tests."""
    FakeDMA.reset_all()
    FakeMemory.reset_all()
    yield
    FakeDMA.reset_all()
    FakeMemory.reset_all()


@pytest.fixture(autouse=True)
def reset_ticks():
    """Return the clock to zero so each test starts from a known time."""
    ticks.now = 0
    yield
    ticks.now = 0


@pytest.fixture(autouse=True)
def quiet_logging():
    """Keep the library's logging off so test output stays readable."""
    import aye_arr.logging as logging
    logging.level = logging.LOG_NONE
    yield
    logging.level = logging.LOG_NONE
