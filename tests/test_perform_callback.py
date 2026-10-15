"""
Tests for perform_callback, which calls a binding with or without its extras.

A binding is either a callable or a callable paired with parameters, and the
receiver offers the event time and the last press time on top. A callback that
does not want those is called again without them, which it recognises from the
TypeError MicroPython raises. CPython words that error differently, so the
narrow-callback path is exercised through a callable that raises MicroPython's
wording rather than through a plain narrow function.
"""

import pytest

from aye_arr.nec.receive import perform_callback


class RefusesExtras:
    """A callable rejecting extra arguments as MicroPython reports it."""

    def __init__(self, accepts=0):
        self.accepts = accepts
        self.calls = []

    def __call__(self, *args):
        if len(args) > self.accepts:
            raise TypeError(f"function takes {self.accepts} positional arguments but {len(args)} were given")
        self.calls.append(args)
        return "called"


class TestCallableForms:
    def test_a_bare_callable_receives_the_extras(self):
        received = []
        perform_callback(lambda *args: received.append(args), 100, 200)

        assert received == [(100, 200)]

    def test_a_tuple_binding_passes_its_parameter_first(self):
        received = []
        perform_callback((lambda *args: received.append(args), "UP"), 100, 200)

        assert received == [("UP", 100, 200)]

    def test_a_list_binding_behaves_as_a_tuple_one(self):
        received = []
        perform_callback([lambda *args: received.append(args), "UP"], 100, 200)

        assert received == [("UP", 100, 200)]

    def test_several_parameters_are_all_passed(self):
        received = []
        perform_callback((lambda *args: received.append(args), 1, 2, 3), 100)

        assert received == [(1, 2, 3, 100)]

    def test_no_extras_leaves_only_the_parameters(self):
        received = []
        perform_callback((lambda *args: received.append(args), "UP"))

        assert received == [("UP",)]

    def test_the_return_value_is_passed_back(self):
        assert perform_callback(lambda *args: "result", 100, 200) == "result"


class TestNarrowCallbacks:
    """A callback that will not take the extras is called without them."""

    def test_a_callback_refusing_extras_is_called_plainly(self):
        callback = RefusesExtras()
        perform_callback(callback, 100, 200)

        assert callback.calls == [()]

    def test_a_parameter_survives_the_retry(self):
        callback = RefusesExtras(accepts=1)
        perform_callback((callback, "UP"), 100, 200)

        assert callback.calls == [("UP",)]

    def test_the_retry_return_value_is_passed_back(self):
        assert perform_callback(RefusesExtras(), 100, 200) == "called"


class TestErrorPropagation:
    def test_an_unrelated_type_error_is_raised(self):
        def callback(*args):
            raise TypeError("something else went wrong")

        with pytest.raises(TypeError, match="something else went wrong"):
            perform_callback(callback, 100, 200)

    def test_a_non_type_error_is_raised(self):
        def callback(*args):
            raise ValueError("a different failure")

        with pytest.raises(ValueError):
            perform_callback(callback, 100, 200)

    def test_an_error_from_the_retry_is_raised(self):
        class FailsBothWays(RefusesExtras):
            def __call__(self, *args):
                if len(args) > 0:
                    raise TypeError("function takes 0 positional arguments but 2 were given")
                raise ValueError("failed without extras")

        with pytest.raises(ValueError, match="failed without extras"):
            perform_callback(FailsBothWays(), 100, 200)
