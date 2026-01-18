#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from typing import Optional

from PySide6.QtCore import QThread
from pynput.mouse import Button, Listener

from src.signal import MouseSignals


class MouseListenerThread(QThread):
    def __init__(self, signals: MouseSignals):
        super().__init__()
        self.signals = signals
        self.listener: Optional[Listener] = None

    def run(self, /):
        self.listener = Listener(on_click=self.on_click)
        self.listener.start()

    def on_click(self, _, __, button: Optional[Button], pressed: bool) -> None:
        if button is None:
            return
        if pressed:
            self.signals.mouse_clicked.emit(str(button))
        else:
            self.signals.mouse_released.emit(str(button))
