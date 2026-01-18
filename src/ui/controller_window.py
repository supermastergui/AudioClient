#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from re import compile

from PySide6.QtWidgets import QWidget

from src.core import VoiceClient
from src.model import ConnectionState
from src.utils import clear_error
from .form import Ui_ControllerWindow
from src.core.voice.transmitter import Transmitter

frequency_pattern = compile(r"\d{1,3}\.\d{1,3}")


class ControllerWindow(QWidget, Ui_ControllerWindow):
    def __init__(self, voice_client: VoiceClient):
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
        self.voice_client.signals.update_current_frequency.connect(
            lambda x: self.label_current_freq_v.setText(f"{x / 1000:.3f}" if x != 0 else "---.---")
        )
        self._frequency = -1
        self.line_edit_freq.textChanged.connect(self.decode_frequency)

        self.transmitters = [
            Transmitter(0, 0),
            Transmitter(122800, 1),
            Transmitter(121500, 2),
            Transmitter(1, 3),
        ]

    def decode_frequency(self, text: str):
        if frequency_pattern.match(text) is not None:
            self.button_freq_rx.setEnabled(True)
            self.button_freq_tx.setEnabled(True)
            self._frequency = int(float(text) * 1000)
            self.transmitters[3].frequency = self._frequency
            self.voice_client.update_transmitter(self.transmitters[3])
        else:
            self._frequency = -1
            self.button_freq_rx.active = False
            self.button_freq_tx.active = False
            self.button_freq_rx.setEnabled(False)
            self.button_freq_tx.setEnabled(False)
            self.voice_client.update_transmitter(1, 122800, False)

    def freq_tx_click(self):
        clear_error(self.line_edit_freq)
        self.button_emer_freq_tx.active = False
        self.button_main_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        if self.button_freq_tx.active:
            self.voice_client.update_transmitter(3, self._frequency, self.button_freq_rx.active)

    def freq_rx_click(self):
        self.transmitters[3].receive_flag = self.button_freq_rx.active

    def main_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_emer_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        if self.button_main_freq_tx.active:
            self.voice_client.update_transmitter(0, self.voice_client.client_info.main_frequency,
                                                 self.button_main_freq_rx.active)

    def main_freq_rx_click(self):
        self.transmitters[0].receive_flag = self.button_main_freq_rx.active

    def unicom_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_emer_freq_tx.active = False
        self.button_main_freq_tx.active = False
        if self.button_unicom_freq_tx.active:
            self.voice_client.update_transmitter(1, 122800, self.button_unicom_freq_rx.active)

    def unicom_freq_rx_click(self):
        self.transmitters[1].receive_flag = self.button_unicom_freq_rx.active

    def emer_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_main_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        if self.button_emer_freq_tx.active:
            self.voice_client.update_transmitter(2, 121500, self.button_emer_freq_rx.active)

    def emer_freq_rx_click(self):
        self.transmitters[2].receive_flag = self.button_emer_freq_rx.active

    def connect_state_changed(self, state: ConnectionState):
        if not self.voice_client.client_info.is_atc:
            return
        if state == ConnectionState.READY:
            self.transmitters[0].frequency = self.voice_client.client_info.main_frequency
            self.voice_client.add_transmitter(self.transmitters[0], False, True)
            self.voice_client.add_transmitter(self.transmitters[1], False, True)
            self.voice_client.add_transmitter(self.transmitters[2], False, True)
            self.voice_client.add_transmitter(self.transmitters[3], False, False)
            self.label_main_freq_v.setText(f"{self.voice_client.client_info.main_frequency / 1000:.3f}")
            self.button_main_freq_rx.active = True
            self.button_unicom_freq_rx.active = True
            self.button_emer_freq_rx.active = True
            self.button_freq_rx.active = False
            self.button_freq_rx.setEnabled(False)
            self.button_freq_tx.setEnabled(False)
