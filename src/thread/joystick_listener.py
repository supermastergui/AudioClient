#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from os import environ

from PySide6.QtCore import QThread
from pygame import JOYBUTTONDOWN, JOYBUTTONUP, event, init, joystick

from src.signal import JoystickSignals


class JoystickListenerThread(QThread):
    def __init__(self, signals: JoystickSignals):
        super().__init__()
        self.signals = signals
        self._running = False
        self._joysticks: dict[int, joystick.JoystickType] = {}

    def scan_joysticks(self):
        self._joysticks.clear()
        for i in range(joystick.get_count()):
            j = joystick.Joystick(i)
            j.init()
            self._joysticks[i] = j

    def run(self, /):
        environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        environ['SDL_VIDEODRIVER'] = 'dummy'
        environ['SDL_AUDIODRIVER'] = 'dummy'

        init()
        joystick.init()

        self.scan_joysticks()

        self._running = True

        while self._running:
            try:
                for e in event.get():
                    if joystick.get_count() != len(self._joysticks):
                        self.scan_joysticks()
                    if e.type == JOYBUTTONDOWN:
                        self.signals.button_pressed.emit(f"{self._joysticks[e.joy].get_name()}.{e.button}")
                        continue
                    if e.type == JOYBUTTONUP:
                        self.signals.button_released.emit(f"{self._joysticks[e.joy].get_name()}.{e.button}")
                self.msleep(10)
            except Exception:
                break

        joystick.quit()

    def stop(self):
        self._running = False
