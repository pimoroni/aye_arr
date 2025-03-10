# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .descriptor import RemoteDescriptor


class PimoroniRemote(RemoteDescriptor):
    NAME = "Pimoroni"

    ADDRESS = 0x00

    BUTTON_CODES = {
        "POWER": 0x45,
        "MODE": 0x46,
        "MUTE": 0x47,
        "PLAY": 0x44,
        "PREV": 0x40,
        "NEXT": 0x43,
        "EQ": 0x07,
        "MINUS": 0x15,
        "PLUS": 0x09,
        "ZERO": 0x16,
        "S": 0x19,
        "SCAN": 0x0d,
        "ONE": 0x0c,
        "TWO": 0x18,
        "THREE": 0x5e,
        "FOUR": 0x08,
        "FIVE": 0x1c,
        "SIX": 0x5a,
        "SEVEN": 0x42,
        "EIGHT": 0x52,
        "NINE": 0x4a
        }

    def __init__(self):
        super().__init__()
