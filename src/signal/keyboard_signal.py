#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from PySide6.QtCore import QObject, Signal


class KeyBoardSignals(QObject):
    key_pressed = Signal(str)
    key_released = Signal(str)

