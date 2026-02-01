#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from PySide6.QtCore import QPoint, Qt, SignalInstance
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget

from .form.generate.sub_window import Ui_SubWindow
from ..signal.sub_window_signals import SubWindowSignals


class SubWindow(QWidget, Ui_SubWindow):
    def __init__(self, signals: SubWindowSignals):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint
                           | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.drag = False
        self.mouse_start_pt = QPoint()
        self.window_pos = QPoint()

        self.signals = signals
        self.button_full_window.clicked.connect(self.full_window)
        self.signals.show_small_window.connect(self.show)

    def full_window(self):
        self.hide()
        self.signals.show_full_window.emit()  # type: ignore

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_start_pt = event.globalPosition().toPoint()
            self.window_pos = self.frameGeometry().topLeft()
            self.drag = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag:
            distance = event.globalPosition().toPoint() - self.mouse_start_pt
            self.move(self.window_pos + distance)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = False
