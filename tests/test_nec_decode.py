"""
Tests for the NEC receiver's extraction of a code from received pulses.

The extraction step is a private method, and MicroPython would reach it by its
plain name. CPython mangles, so it is called here as
`_NECReceiver__extract_code`, which is why these tests do not go through
`decode` and its callbacks.

TestRoundTrip is the pairing that matters most, feeding the sender's own pulse
durations back through the receiver.
"""

import pytest

from aye_arr.nec.common import NEC_DATA_BURST_US, NEC_DATA_ONE_US, NEC_DATA_ZERO_US, NEC_NONE, NEC_REPEAT, NEC_START_BURST_US, NEC_START_DATA_US, NEC_START_REPEAT_US
from aye_arr.nec.receive import NECReceiver
from aye_arr.nec.remotes import PimoroniRemote
from aye_arr.nec.send import NECSender
from aye_arr.pulse.common import Pulse
from aye_arr.pulse.send import PulseSender

# A received code is a start pulse followed by one pulse per bit
CODE_PULSE_COUNT = 33


@pytest.fixture
def extract():
    """The receiver's code extraction, reached through its mangled name."""
    receiver = NECReceiver(pin_num=3, pio=1, sm=0)
    return receiver._NECReceiver__extract_code


def pulses_for_code(code):
    """The pulse sequence a remote sends for a code, least significant bit first."""
    pulses = [Pulse(NEC_START_BURST_US, NEC_START_DATA_US)]
    for bit in range(32):
        idle = NEC_DATA_ONE_US if code & (1 << bit) else NEC_DATA_ZERO_US
        pulses.append(Pulse(NEC_DATA_BURST_US, idle))
    return pulses


def sent_pulses(code=None, addr_cmd=None):
    """The durations NECSender emits, as pulses, with its final burst dropped."""
    recorded = []
    original_send = PulseSender.send
    original_wait = PulseSender.wait_for_send
    PulseSender.send = lambda self, burst_us, idle_us: recorded.append(Pulse(burst_us, idle_us))
    PulseSender.wait_for_send = lambda self: None
    try:
        sender = NECSender(pin_num=2, pio=0, sm=1)
        sender.start()
        if addr_cmd is not None:
            sender.send_addr_cmd(*addr_cmd)
        else:
            sender.send_code(code)
    finally:
        PulseSender.send = original_send
        PulseSender.wait_for_send = original_wait

    # The final burst's idle outruns the receiver's counter, so it arrives as a
    # timeout that ends the sequence instead of as a pulse
    return recorded[:CODE_PULSE_COUNT]


class TestValidCodes:
    @pytest.mark.parametrize("code", [
        0x00000000,
        0xffffffff,
        0x00000001,
        0x80000000,
        0xb946ff00,
        0x0000ffff,
        0xdeadbeef,
    ])
    def test_a_code_is_extracted_from_its_pulses(self, extract, code):
        assert extract(pulses_for_code(code)) == code

    def test_a_sequence_of_the_expected_length_is_accepted(self, extract):
        assert len(pulses_for_code(0)) == CODE_PULSE_COUNT

    def test_extra_trailing_pulses_are_ignored(self, extract):
        pulses = pulses_for_code(0xb946ff00)
        pulses.append(Pulse(NEC_DATA_BURST_US, NEC_DATA_ZERO_US))

        assert extract(pulses) == 0xb946ff00


class TestRoundTrip:
    """What the sender emits is what the receiver reads back."""

    @pytest.mark.parametrize("code", [0x00000000, 0xffffffff, 0xb946ff00, 0x12345678])
    def test_a_sent_code_is_received(self, extract, code):
        assert extract(sent_pulses(code=code)) == code

    @pytest.mark.parametrize("addr,cmd", [(0x00, 0x46), (0x04, 0x00), (0xff, 0xff)])
    def test_a_sent_address_and_command_is_received(self, extract, addr, cmd):
        code = extract(sent_pulses(addr_cmd=(addr, cmd)))

        assert code & 0xff == addr
        assert (code >> 8) & 0xff == addr ^ 0xff
        assert (code >> 16) & 0xff == cmd
        assert (code >> 24) & 0xff == cmd ^ 0xff

    def test_a_sent_remote_button_is_received(self, extract):
        addr, cmd = PimoroniRemote.ADDRESS, PimoroniRemote.BUTTON_CODES["UP"]
        code = extract(sent_pulses(addr_cmd=(addr, cmd)))

        assert code & 0xff == addr
        assert (code >> 16) & 0xff == cmd


class TestRepeats:
    def test_a_lone_repeat_pulse_is_a_repeat(self, extract):
        assert extract([Pulse(NEC_START_BURST_US, NEC_START_REPEAT_US)]) == NEC_REPEAT

    def test_a_repeat_is_not_a_code(self, extract):
        assert NEC_REPEAT != NEC_NONE

    def test_a_repeat_pulse_with_data_after_it_is_not_a_repeat(self, extract):
        pulses = [Pulse(NEC_START_BURST_US, NEC_START_REPEAT_US),
                  Pulse(NEC_DATA_BURST_US, NEC_DATA_ZERO_US)]

        assert extract(pulses) is None


class TestRejection:
    def test_no_pulses_gives_no_code(self, extract):
        assert extract([]) is None

    def test_a_short_sequence_gives_no_code(self, extract):
        assert extract(pulses_for_code(0)[:-1]) is None

    def test_a_start_pulse_alone_gives_no_code(self, extract):
        assert extract([Pulse(NEC_START_BURST_US, NEC_START_DATA_US)]) is None

    def test_an_invalid_start_is_skipped(self, extract):
        pulses = [Pulse(100, 100)] + pulses_for_code(0xb946ff00)

        assert extract(pulses) == 0xb946ff00

    def test_several_invalid_starts_are_skipped(self, extract):
        pulses = [Pulse(100, 100), Pulse(50, 75), Pulse(120, 30)] + pulses_for_code(0x0000ffff)

        assert extract(pulses) == 0x0000ffff

    def test_an_invalid_start_consumes_the_pulse(self, extract):
        pulses = [Pulse(100, 100)] + pulses_for_code(0)
        extract(pulses)

        assert len(pulses) == CODE_PULSE_COUNT

    def test_an_invalid_data_pulse_gives_no_code(self, extract):
        pulses = pulses_for_code(0)
        pulses[5] = Pulse(NEC_DATA_BURST_US, 5000)

        assert extract(pulses) is None

    def test_a_data_pulse_between_the_two_bands_gives_no_code(self, extract):
        # Each band is a share of its own length, so the gap between them sits
        # above the midpoint of a zero and a one
        zero_total = NEC_DATA_BURST_US + NEC_DATA_ZERO_US
        one_total = NEC_DATA_BURST_US + NEC_DATA_ONE_US
        between = (zero_total * 1.3 + one_total * 0.7) / 2

        pulses = pulses_for_code(0)
        pulses[1] = Pulse(NEC_DATA_BURST_US, between - NEC_DATA_BURST_US)

        assert extract(pulses) is None

    def test_the_midpoint_of_a_zero_and_a_one_reads_as_a_one(self, extract):
        # The one's band is the wider of the two, so it claims the midpoint
        pulses = pulses_for_code(0)
        pulses[1] = Pulse(NEC_DATA_BURST_US, (NEC_DATA_ZERO_US + NEC_DATA_ONE_US) // 2)

        assert extract(pulses) == 0x00000001


class TestTolerance:
    """A pulse is matched on its total length, within the allowed deviation."""

    @pytest.mark.parametrize("factor", [0.8, 0.9, 1.0, 1.1, 1.2])
    def test_stretched_data_pulses_still_decode(self, extract, factor):
        pulses = [Pulse(NEC_START_BURST_US, NEC_START_DATA_US)]
        for bit in range(32):
            idle = NEC_DATA_ONE_US if 0xb946ff00 & (1 << bit) else NEC_DATA_ZERO_US
            pulses.append(Pulse(NEC_DATA_BURST_US * factor, idle * factor))

        assert extract(pulses) == 0xb946ff00

    def test_a_burst_and_idle_trade_against_each_other(self, extract):
        # Only the combined length is checked, so a long burst offsets a short idle
        pulses = pulses_for_code(0)
        pulses[1] = Pulse(NEC_DATA_BURST_US + 200, NEC_DATA_ZERO_US - 200)

        assert extract(pulses) == 0
