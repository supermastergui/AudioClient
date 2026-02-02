#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from PySide6.QtCore import Qt

from src.signal import AudioClientSignals
from .component.frameless_widget import FramelessWidget
from .form import Ui_SubWindow


class SubWindow(FramelessWidget, Ui_SubWindow):
    def __init__(self, signals: AudioClientSignals):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.signals = signals
        self.button_full_window.clicked.connect(self.full_window)
        self.signals.show_small_window.connect(self.show)

    def full_window(self):
        self.hide()
        self.signals.show_full_window.emit()  # type: ignore
