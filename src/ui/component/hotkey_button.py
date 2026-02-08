from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from src.signal import JoystickSignals, KeyBoardSignals, MouseSignals


class HotkeyButton(QPushButton):
    def __init__(self,
                 parent=None,
                 shown_key: str = "CTRL_L",
                 select_message: str = "...",
                 ignore_keys: Optional[list[str]] = None,
                 cancel_keys: Optional[list[str]] = None):
        super().__init__(parent)
        if ignore_keys is None:
            self._ignore_keys = ["Button.left", "Button.right"]
        if cancel_keys is None:
            self._cancel_keys = ["Key.esc"]
        self._keyboard_signal: Optional[KeyBoardSignals] = None
        self._mouse_signal: Optional[MouseSignals] = None
        self._joystick_signal: Optional[JoystickSignals] = None

        self._select_message = select_message
        self._start_select = False
        self._selected_key = shown_key
        self.setText(shown_key)
        self.clicked.connect(self.select_key)

    def handle_button_press(self, button: str) -> None:
        if not self._start_select:
            return
        if button in self._cancel_keys:
            self._start_select = False
            self.setText(self._selected_key)
            return
        if button in self._ignore_keys:
            return
        self._start_select = False
        self._selected_key = button
        self.setText(self._selected_key)

    def select_key(self) -> None:
        self.setText(self._select_message)
        self._start_select = True

    @property
    def selected_key(self) -> str:
        return self._selected_key

    @selected_key.setter
    def selected_key(self, key: str) -> None:
        self._selected_key = key
        self.setText(self._selected_key)

    @property
    def select_message(self) -> str:
        return self._select_message

    @select_message.setter
    def select_message(self, message: str) -> None:
        self._select_message = message

    @property
    def keyboard_signal(self) -> Optional[KeyBoardSignals]:
        return self._keyboard_signal

    @keyboard_signal.setter
    def keyboard_signal(self, signal: KeyBoardSignals):
        self._keyboard_signal = signal
        self._keyboard_signal.key_pressed.connect(
            self.handle_button_press, Qt.ConnectionType.QueuedConnection
        )

    @property
    def mouse_signal(self) -> Optional[MouseSignals]:
        return self._mouse_signal

    @mouse_signal.setter
    def mouse_signal(self, signal: MouseSignals):
        self._mouse_signal = signal
        self._mouse_signal.mouse_clicked.connect(
            self.handle_button_press, Qt.ConnectionType.QueuedConnection
        )

    @property
    def joystick_signal(self) -> Optional[JoystickSignals]:
        return self._joystick_signal

    @joystick_signal.setter
    def joystick_signal(self, signal: JoystickSignals):
        self._joystick_signal = signal
        self._joystick_signal.button_pressed.connect(
            self.handle_button_press, Qt.ConnectionType.QueuedConnection
        )
