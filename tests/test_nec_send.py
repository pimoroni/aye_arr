"""
Tests for the NEC sender's encoding of codes into pulses.

Most tests capture the pulse durations NECSender asks of the layer beneath it,
which is the protocol boundary worth pinning. TestCountEncoding instead lets the
real PulseSender run so the conversion into the PIO's 16 bit counts is covered.
"""

import pytest

from aye_arr.nec.common import NEC_DATA_BURST_US, NEC_DATA_LOCKOUT_US, NEC_DATA_ONE_US, NEC_DATA_ZERO_US, NEC_FREQUENCY, NEC_START_BURST_US, NEC_START_DATA_US, NEC_START_REPEAT_US
from aye_arr.nec.remotes import PimoroniRemote
from aye_arr.nec.send import NECSender
from aye_arr.pulse.pio.tx import CLOCKS_PER_CYCLE
from aye_arr.pulse.send import PulseSender

START = (NEC_START_BURST_US, NEC_START_DATA_US)
REPEAT_START = (NEC_START_BURST_US, NEC_START_REPEAT_US)
ZERO = (NEC_DATA_BURST_US, NEC_DATA_ZERO_US)
ONE = (NEC_DATA_BURST_US, NEC_DATA_ONE_US)
FINAL = (NEC_DATA_BURST_US, NEC_DATA_LOCKOUT_US)


@pytest.fixture
def sender(monkeypatch):
    """A started sender recording the pulse durations it asks to be sent."""
    pulses = []

    monkeypatch.setattr(PulseSender, "send",
                        lambda self, burst_us, idle_us: pulses.append((burst_us, idle_us)))
    monkeypatch.setattr(PulseSender, "wait_for_send", lambda self: None)

    sender = NECSender(pin_num=2, pio=0, sm=0)
    sender.start()
    sender.pulses = pulses
    return sender


def bits_of(sender):
    """The 32 data pulses, with the start and final pulses removed."""
    return sender.pulses[1:33]


class TestFraming:
    def test_a_code_is_framed_by_a_start_and_a_final_burst(self, sender):
        sender.send_code(0x00000000)

        assert len(sender.pulses) == 34
        assert sender.pulses[0] == START
        assert sender.pulses[-1] == FINAL

    def test_a_repeat_carries_no_data(self, sender):
        sender.send_repeat()

        assert sender.pulses == [REPEAT_START, FINAL]

    def test_a_repeat_start_differs_from_a_code_start(self, sender):
        sender.send_repeat()
        repeat_start = sender.pulses[0]

        sender.pulses.clear()
        sender.send_code(0x00000000)

        assert repeat_start != sender.pulses[0]


class TestDataBits:
    def test_a_zero_code_is_all_zero_bits(self, sender):
        sender.send_code(0x00000000)

        assert bits_of(sender) == [ZERO] * 32

    def test_a_full_code_is_all_one_bits(self, sender):
        sender.send_code(0xffffffff)

        assert bits_of(sender) == [ONE] * 32

    def test_the_least_significant_bit_is_sent_first(self, sender):
        sender.send_code(0x00000001)
        bits = bits_of(sender)

        assert bits[0] == ONE
        assert bits[1:] == [ZERO] * 31

    def test_the_most_significant_bit_is_sent_last(self, sender):
        sender.send_code(0x80000000)
        bits = bits_of(sender)

        assert bits[-1] == ONE
        assert bits[:-1] == [ZERO] * 31

    def test_each_bit_position_is_sent_in_order(self, sender):
        sender.send_code(0x0000ffff)
        bits = bits_of(sender)

        assert bits[:16] == [ONE] * 16
        assert bits[16:] == [ZERO] * 16


class TestAddressAndCommand:
    def test_a_short_address_is_followed_by_its_inverse(self, sender):
        sender.send_addr_cmd(0x00, 0x46)
        from_addr_cmd = list(sender.pulses)

        sender.pulses.clear()
        sender.send_code(0xb946ff00)

        assert from_addr_cmd == sender.pulses

    def test_an_extended_address_is_sent_whole(self, sender):
        sender.send_addr_cmd(0x1234, 0x46)
        from_addr_cmd = list(sender.pulses)

        sender.pulses.clear()
        sender.send_code(0xb9461234)

        assert from_addr_cmd == sender.pulses

    def test_a_command_is_followed_by_its_inverse(self, sender):
        sender.send_addr_cmd(0x04, 0x00)
        from_addr_cmd = list(sender.pulses)

        sender.pulses.clear()
        sender.send_code(0xff00fb04)

        assert from_addr_cmd == sender.pulses

    def test_a_remote_button_is_sent_by_name(self, sender):
        sender.send_remote(PimoroniRemote, "UP")
        from_remote = list(sender.pulses)

        sender.pulses.clear()
        sender.send_addr_cmd(PimoroniRemote.ADDRESS, PimoroniRemote.BUTTON_CODES["UP"])

        assert from_remote == sender.pulses

    def test_an_unknown_button_name_raises(self, sender):
        with pytest.raises(KeyError):
            sender.send_remote(PimoroniRemote, "MISSING")


class TestRangeChecks:
    @pytest.mark.parametrize("addr", [-1, 0x10000])
    def test_an_out_of_range_address_raises(self, sender, addr):
        with pytest.raises(ValueError):
            sender.send_addr_cmd(addr, 0x00)

    @pytest.mark.parametrize("cmd", [-1, 0x100])
    def test_an_out_of_range_command_raises(self, sender, cmd):
        with pytest.raises(ValueError):
            sender.send_addr_cmd(0x00, cmd)

    @pytest.mark.parametrize("code", [-1, 0x100000000])
    def test_an_out_of_range_code_raises(self, sender, code):
        with pytest.raises(ValueError):
            sender.send_code(code)

    @pytest.mark.parametrize("addr,cmd", [(0x0000, 0x00), (0xffff, 0xff)])
    def test_the_range_limits_are_accepted(self, sender, addr, cmd):
        sender.send_addr_cmd(addr, cmd)

        assert len(sender.pulses) == 34


class TestCountEncoding:
    """The real PulseSender converts durations into the PIO's 16 bit counts."""

    def sender_and_sm(self):
        sender = NECSender(pin_num=2, pio=0, sm=0)
        sender.start()
        return sender, sender._PulseSender__sm

    def expected_count(self, us):
        pio_freq = NEC_FREQUENCY * CLOCKS_PER_CYCLE
        return round(((us * pio_freq) / (CLOCKS_PER_CYCLE * 1000000)) - 2)

    def test_a_pulse_packs_its_burst_above_its_idle(self):
        sender, sm = self.sender_and_sm()
        sender.send_repeat()

        burst, idle = (sm.puts[0] >> 16) & 0xffff, sm.puts[0] & 0xffff
        assert burst == self.expected_count(NEC_START_BURST_US)
        assert idle == self.expected_count(NEC_START_REPEAT_US)

    def test_every_count_fits_its_16_bit_field(self):
        sender, sm = self.sender_and_sm()
        sender.send_code(0xffffffff)

        for word in sm.puts:
            assert 0 <= word <= 0xffffffff

    def test_a_code_puts_one_word_per_pulse(self):
        sender, sm = self.sender_and_sm()
        sender.send_code(0x00000000)

        assert len(sm.puts) == 34

    def test_a_one_bit_is_a_longer_idle_than_a_zero(self):
        sender, sm = self.sender_and_sm()
        sender.send_code(0x00000001)

        one_idle = sm.puts[1] & 0xffff
        zero_idle = sm.puts[2] & 0xffff
        assert one_idle > zero_idle


class TestStartRequired:
    def test_sending_before_starting_raises(self):
        sender = NECSender(pin_num=2, pio=0, sm=0)

        with pytest.raises(RuntimeError):
            sender.send_code(0x00000000)

    def test_sending_after_stopping_raises(self):
        sender = NECSender(pin_num=2, pio=0, sm=0)
        sender.start()
        sender.stop()

        with pytest.raises(RuntimeError):
            sender.send_code(0x00000000)


class TestConstruction:
    @pytest.mark.parametrize("pio", [-1, 3])
    def test_an_out_of_range_pio_raises(self, pio):
        with pytest.raises(ValueError):
            NECSender(pin_num=2, pio=pio, sm=0)

    @pytest.mark.parametrize("sm", [-1, 4])
    def test_an_out_of_range_state_machine_raises(self, sm):
        with pytest.raises(ValueError):
            NECSender(pin_num=2, pio=0, sm=sm)
