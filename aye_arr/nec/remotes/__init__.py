# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .argon import ArgonRemote
from .pimoroni import PimoroniRemote
from .lg import LGRemote

KNOWN_REMOTES = (
    ArgonRemote,
    PimoroniRemote,
    LGRemote)
