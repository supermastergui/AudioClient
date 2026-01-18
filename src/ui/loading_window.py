#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from PySide6.QtWidgets import QWidget

from .form import Ui_LoadingWindow
from src.constants import app_title


class LoadingWindow(QWidget, Ui_LoadingWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.title_label.setText(app_title)
        self.setWindowTitle(app_title)
        self.loading_spinner.startAnimation()

    def stop_animation(self) -> None:
        self.loading_spinner.stopAnimation()
