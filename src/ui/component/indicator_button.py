from PySide6.QtWidgets import QPushButton


class IndicatorButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.is_active = False
        self.update_style()

    def set_active(self, active):
        if self.is_active != active:
            self.is_active = active
            self.update_style()

    def update_style(self):
        if self.is_active:
            self.setStyleSheet("background-color: #7ed6df; color: #000000")
        else:
            self.setStyleSheet("")
