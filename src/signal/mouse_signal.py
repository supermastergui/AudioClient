#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from PySide6.QtCore import QObject, Signal


class MouseSignals(QObject):
    mouse_clicked = Signal(str)
    mouse_released = Signal(str)

