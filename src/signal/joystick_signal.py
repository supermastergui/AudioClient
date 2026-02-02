#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from PySide6.QtCore import QObject, Signal


class JoystickSignals(QObject):
    button_pressed = Signal(str)
    button_released = Signal(str)
