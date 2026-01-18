from collections.abc import Callable

from PySide6.QtCore import QObject

from .selected_button import SelectedButton
from src.core.voice.transmitter import Transmitter


class ButtonGroup(QObject):
    def __init__(self, /):
        super().__init__()
        self.buttons: dict[str, SelectedButton] = {}

    def add_button(self, button: SelectedButton):
        self.buttons[button.text()] = button

    def remove_button(self, button: SelectedButton):
        del self.buttons[button.text()]

    def activate(self, button: SelectedButton):
        if button.text() not in self.buttons:
            return
        for item in self.buttons.values():
            if button != item:
                item.active = False
        button.active = True

    def deactivate(self, button: SelectedButton):
        if button.text() not in self.buttons:
            return
        button.active = False


class SelectedButtonWithTransmitter(SelectedButton):
    def __init__(self, transmitter: Transmitter, active_callback: Callable[[Transmitter, bool], None], /):
        super().__init__()
        self.transmitter = transmitter
        self.active_callback = active_callback

    @property
    def active(self) -> bool:
        return super().active

    @active.setter
    def active(self, value: bool):
        super().active = value
        self.active_callback(self.transmitter, value)
