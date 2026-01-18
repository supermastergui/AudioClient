#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from typing import Optional, Union

from PySide6.QtCore import QThread
from pynput.keyboard import Key, KeyCode, Listener

from src.signal import KeyBoardSignals


class KeyboardListenerThread(QThread):
    def __init__(self, signals: KeyBoardSignals):
        super().__init__()
        self.signals = signals
        self.listener: Optional[Listener] = None

    def run(self, /):
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, button: Optional[Union[Key, KeyCode]]) -> None:
        if button is None:
            return
        self.signals.key_pressed.emit(str(button))

    def on_release(self, button: Optional[Union[Key, KeyCode]]) -> None:
        if button is None:
            return
        self.signals.key_released.emit(str(button))
