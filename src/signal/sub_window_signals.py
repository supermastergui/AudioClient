#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from PySide6.QtCore import QObject, Signal


class SubWindowSignals(QObject):
    show_full_window = Signal()
    show_small_window = Signal()
