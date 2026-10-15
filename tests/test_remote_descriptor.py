"""
Tests for RemoteDescriptor's button binding and for the shipped remotes.

RemoteDescriptor is plain Python with no MicroPython dependency, so it is
exercised directly. The shipped remotes are checked for the properties the
receiver relies on when it matches a command against them.
"""

import pytest

from aye_arr.nec.remotes import KNOWN_REMOTES, ArgonRemote, LGRemote, PimoroniRemote, RemoteDescriptor


class ExampleRemote(RemoteDescriptor):
    NAME = "Example"
    ADDRESS = 0x1f
    BUTTON_CODES = {"UP": 0x11, "DOWN": 0x22, "OK": 0x33}
    NUMBERS = {"UP": 1, "DOWN": 2}


def press():
    pass


def repeat():
    pass


def release():
    pass


def short():
    pass


class TestBinding:
    def test_a_bound_name_is_reachable_by_its_code(self):
        remote = ExampleRemote()
        remote.bind("UP", press)

        assert remote.button(0x11).on_press is press

    def test_a_bound_code_needs_no_name(self):
        remote = ExampleRemote()
        remote.bind_code(0x99, press)

        assert remote.button(0x99).on_press is press

    def test_all_four_actions_are_stored_in_order(self):
        remote = ExampleRemote()
        remote.bind("UP", press, short, repeat, release)
        button = remote.button(0x11)

        assert button.on_press is press
        assert button.on_short is short
        assert button.on_repeat is repeat
        assert button.on_release is release

    def test_an_unbound_name_raises(self):
        remote = ExampleRemote()

        with pytest.raises(KeyError):
            remote.bind("MISSING", press)

    def test_binding_a_code_twice_raises(self):
        remote = ExampleRemote()
        remote.bind("UP", press)

        with pytest.raises(ValueError):
            remote.bind_code(0x11, press)

    def test_an_unbound_code_raises_when_read(self):
        remote = ExampleRemote()

        with pytest.raises(KeyError):
            remote.button(0x11)

    def test_bindings_are_per_instance(self):
        bound = ExampleRemote()
        bound.bind("UP", press)

        with pytest.raises(KeyError):
            ExampleRemote().button(0x11)


class TestRepeatSentinel:
    """`on_repeat=True` asks for the press action to be repeated."""

    def test_true_reuses_the_press_action(self):
        remote = ExampleRemote()
        remote.bind("UP", press)

        assert remote.button(0x11).on_repeat is press

    def test_a_callable_is_kept_as_given(self):
        remote = ExampleRemote()
        remote.bind("UP", press, on_repeat=repeat)

        assert remote.button(0x11).on_repeat is repeat

    def test_none_leaves_no_repeat_action(self):
        remote = ExampleRemote()
        remote.bind("UP", press, on_repeat=None)

        assert remote.button(0x11).on_repeat is None


class TestUnbinding:
    def test_a_name_can_be_unbound(self):
        remote = ExampleRemote()
        remote.bind("UP", press)
        remote.unbind("UP")

        with pytest.raises(KeyError):
            remote.button(0x11)

    def test_a_code_can_be_unbound(self):
        remote = ExampleRemote()
        remote.bind_code(0x99, press)
        remote.unbind_code(0x99)

        with pytest.raises(KeyError):
            remote.button(0x99)

    def test_an_unknown_name_raises(self):
        remote = ExampleRemote()

        with pytest.raises(KeyError):
            remote.unbind("MISSING")

    def test_a_name_can_be_rebound_after_unbinding(self):
        remote = ExampleRemote()
        remote.bind("UP", press)
        remote.unbind("UP")
        remote.bind("UP", repeat)

        assert remote.button(0x11).on_press is repeat


class TestDefaults:
    def test_the_base_carries_empty_tables(self):
        assert RemoteDescriptor.BUTTON_CODES == {}
        assert RemoteDescriptor.NUMBERS == {}

    def test_the_general_callbacks_start_unset(self):
        remote = ExampleRemote()

        assert remote.on_known is None
        assert remote.on_any is None


class TestShippedRemotes:
    @pytest.mark.parametrize("remote_type", [ArgonRemote, LGRemote, PimoroniRemote])
    def test_a_remote_names_itself(self, remote_type):
        assert remote_type.NAME != RemoteDescriptor.NAME
        assert remote_type.BUTTON_CODES

    @pytest.mark.parametrize("remote_type", [ArgonRemote, LGRemote, PimoroniRemote])
    def test_codes_are_unique(self, remote_type):
        # The receiver matches a command by scanning for the first equal code,
        # so a repeated code would make one of its names unreachable
        codes = list(remote_type.BUTTON_CODES.values())
        assert len(codes) == len(set(codes))

    @pytest.mark.parametrize("remote_type", [ArgonRemote, LGRemote, PimoroniRemote])
    def test_codes_are_single_bytes(self, remote_type):
        for code in remote_type.BUTTON_CODES.values():
            assert 0x00 <= code <= 0xff

    @pytest.mark.parametrize("remote_type", [ArgonRemote, LGRemote, PimoroniRemote])
    def test_addresses_are_single_bytes(self, remote_type):
        assert 0x00 <= remote_type.ADDRESS <= 0xff

    @pytest.mark.parametrize("remote_type", [ArgonRemote, LGRemote, PimoroniRemote])
    def test_numbers_name_bound_buttons(self, remote_type):
        for name in remote_type.NUMBERS:
            assert name in remote_type.BUTTON_CODES

    @pytest.mark.parametrize("remote_type", [ArgonRemote, LGRemote, PimoroniRemote])
    def test_numbers_are_single_digits(self, remote_type):
        digits = list(remote_type.NUMBERS.values())
        assert digits == [] or sorted(digits) == list(range(10))

    @pytest.mark.parametrize("remote_type", [ArgonRemote, LGRemote, PimoroniRemote])
    def test_a_shipped_remote_is_known(self, remote_type):
        # The receiver suggests a remote from this list when a code is unmatched
        assert remote_type in KNOWN_REMOTES

    @pytest.mark.parametrize("remote_type", [ArgonRemote, LGRemote, PimoroniRemote])
    def test_a_shipped_remote_binds_its_own_names(self, remote_type):
        remote = remote_type()
        for name, code in remote_type.BUTTON_CODES.items():
            remote.bind(name, press)
            assert remote.button(code).on_press is press
