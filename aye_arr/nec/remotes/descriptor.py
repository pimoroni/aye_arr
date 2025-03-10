# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from collections import namedtuple

ButtonHandler = namedtuple("ButtonHandler", ("on_press", "on_repeat", "on_release"))


class RemoteDescriptor:
    NAME = "Unknown"
    ADDRESS = 0x00
    BUTTON_CODES = {}

    def __init__(self):
        self.__buttons = {}

    def bind(self, name, on_press, on_repeat=True, on_release=False):
        if name not in self.BUTTON_CODES:
            raise KeyError(f"Name '{name}' is not a bindable button of the '{self.NAME}' remote")

        self.__bind(self.BUTTON_CODES[name], on_press,
                    on_press if on_repeat is True else on_repeat,
                    None if on_release is False else on_release)

    def __bind(self, code, on_press, on_repeat, on_release):
        if code in self.__buttons:
            raise ValueError(f"A button with the code '0x{code:0x}' is already bound to the '{self.NAME}' remote. Use a different code")
        self.__buttons[code] = ButtonHandler(on_press, on_repeat, on_release)

    def unbind(self, name):
        if name not in self.BUTTON_CODES:
            raise KeyError(f"Name '{name}' is not a bindable button of the '{self.NAME}' remote")

        self.__unbind(self.BUTTON_CODES[name])

    def __unbind(self, code):
        del self.__buttons[code]

    def button(self, code):
        return self.__buttons[code]
