#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from src.core import VoiceClient
from src.model import ConnectionState
from src.utils import clear_error, show_error
from .form import Ui_ControllerWindow
from src.core.voice.transmitter import Transmitter
from .sub_window import SubWindow
from ..signal.sub_window_signals import SubWindowSignals


class ControllerWindow(QWidget, Ui_ControllerWindow):
    def __init__(self, voice_client: VoiceClient, signals: SubWindowSignals):
        super().__init__()
        self.setupUi(self)
        self.voice_client = voice_client
        self.button_main_freq_tx.clicked.connect(self.main_freq_tx_click)
        self.button_main_freq_rx.clicked.connect(self.main_freq_rx_click)
        self.button_unicom_freq_tx.clicked.connect(self.unicom_freq_tx_click)
        self.button_unicom_freq_rx.clicked.connect(self.unicom_freq_rx_click)
        self.button_emer_freq_tx.clicked.connect(self.emer_freq_tx_click)
        self.button_emer_freq_rx.clicked.connect(self.emer_freq_rx_click)
        self.button_freq_tx.clicked.connect(self.freq_tx_click)
        self.button_freq_rx.clicked.connect(self.freq_rx_click)
        self.voice_client.signals.connection_state_changed.connect(self.connect_state_changed)
        self.voice_client.signals.update_current_frequency.connect(self.set_current_frequency)
        self._frequency = -1
        self.line_edit_freq.editingFinished.connect(self.decode_frequency)

        self._main_transmitter = Transmitter(0, 0)
        self._unicom_transmitter = Transmitter(122800, 1)
        self._emer_transmitter = Transmitter(121500, 2)
        self._custom_transmitter = Transmitter(0, 3)

        self.sub_window = SubWindow(signals)
        self.signals = signals
        self.button_small_window.clicked.connect(self.small_window)

    def small_window(self):
        self.signals.show_small_window.emit()

    def set_current_frequency(self, frequency: int):
        freq = f"{frequency / 1000:.3f}" if frequency != 0 else "---.---"
        self.label_current_freq_v.setText(freq)
        self.sub_window.label_current_freq_v.setText(freq)

    def decode_frequency(self):
        frequency = int(float(self.line_edit_freq.text()) * 1000)
        if frequency < 3000 or frequency > 200000:
            show_error(self.line_edit_freq)
            self._frequency = -1
            self.button_freq_rx.active = False
            self.button_freq_tx.active = False
            self.button_freq_rx.setEnabled(False)
            self.button_freq_tx.setEnabled(False)
            return
        clear_error(self.line_edit_freq)
        self.button_freq_rx.setEnabled(True)
        self.button_freq_tx.setEnabled(True)
        self._frequency = frequency
        self._custom_transmitter.frequency = self._frequency
        self.voice_client.update_transmitter(self._custom_transmitter)

    def freq_tx_click(self):
        self.button_emer_freq_tx.active = False
        self.button_main_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        self._custom_transmitter.send_flag = self.button_freq_tx.active
        self.voice_client.update_transmitter(self._custom_transmitter)

    def freq_rx_click(self):
        self._custom_transmitter.receive_flag = self.button_freq_rx.active
        self.voice_client.update_transmitter(self._custom_transmitter)

    def main_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_emer_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        self._main_transmitter.send_flag = self.button_main_freq_tx.active
        self.voice_client.update_transmitter(self._main_transmitter)

    def main_freq_rx_click(self):
        self._main_transmitter.receive_flag = self.button_main_freq_rx.active
        self.voice_client.update_transmitter(self._main_transmitter)

    def unicom_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_emer_freq_tx.active = False
        self.button_main_freq_tx.active = False
        self._unicom_transmitter.send_flag = self.button_unicom_freq_tx.active
        self.voice_client.update_transmitter(self._unicom_transmitter)

    def unicom_freq_rx_click(self):
        self._unicom_transmitter.receive_flag = self.button_unicom_freq_rx.active
        self.voice_client.update_transmitter(self._unicom_transmitter)

    def emer_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_main_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        self._emer_transmitter.send_flag = self.button_emer_freq_tx.active
        self.voice_client.update_transmitter(self._emer_transmitter)

    def emer_freq_rx_click(self):
        self._emer_transmitter.receive_flag = self.button_emer_freq_rx.active
        self.voice_client.update_transmitter(self._emer_transmitter)

    def clear(self):
        self.label_main_freq_v.setText("---.---")

        self._main_transmitter.clear()
        self._unicom_transmitter.clear()
        self._emer_transmitter.clear()
        self._custom_transmitter.clear()

        self.button_freq_tx.active = False
        self.button_main_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        self.button_emer_freq_tx.active = False

        self.button_main_freq_rx.active = False
        self.button_unicom_freq_rx.active = False
        self.button_emer_freq_rx.active = False
        self.button_freq_rx.active = False

        self.button_freq_tx.setEnabled(False)
        self.button_freq_rx.setEnabled(False)

    def connect_state_changed(self, state: ConnectionState):
        if not self.voice_client.client_info.is_atc:
            return
        if state == ConnectionState.READY:
            self.clear()
            self._main_transmitter.frequency = self.voice_client.client_info.main_frequency
            self.voice_client.add_transmitter(self._main_transmitter)
            self.voice_client.add_transmitter(self._unicom_transmitter)
            self.voice_client.add_transmitter(self._emer_transmitter)
            self.voice_client.add_transmitter(self._custom_transmitter)
            self.label_main_freq_v.setText(f"{self.voice_client.client_info.main_frequency / 1000:.3f}")
        elif state == ConnectionState.DISCONNECTED:
            self.clear()
