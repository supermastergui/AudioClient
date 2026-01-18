#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from threading import Event, Thread
from time import sleep

from PySide6.QtWidgets import QWidget
from loguru import logger

from .form import Ui_ClientWindow
from ..core import VoiceClient
from ..core.fsuipc_client import FSUIPCClient
from src.core.voice.transmitter import Transmitter


class ClientWindow(QWidget, Ui_ClientWindow):
    def __init__(self, voice_client: VoiceClient, fsuipc_client: FSUIPCClient):
        super().__init__()
        self.setupUi(self)

        self.button_com1_tx.clicked.connect(self.com1_freq_tx_clicked)
        self.button_com2_tx.clicked.connect(self.com2_freq_tx_clicked)

        self.voice_client = voice_client
        self.fsuipc_client = fsuipc_client
        self.thread_exit = Event()
        self.com1_transmitter = Transmitter(122800, False)
        self.com2_transmitter = Transmitter(121500, False)

    def set_com1_frequency(self, frequency: int):
        self.fsuipc_client.set_com1_frequency(frequency)
        self.com1_transmitter.frequency = frequency

    def set_com2_frequency(self, frequency: int):
        self.fsuipc_client.set_com2_frequency(frequency)
        self.com2_transmitter.frequency = frequency

    def com1_freq_tx_clicked(self):
        self.button_com2_tx.active = False
        if self.button_com1_tx.active:
            self.voice_client.update_transmitter(self.com1_transmitter)

    def com2_freq_tx_clicked(self):
        self.button_com1_tx.active = False
        if self.button_com2_tx.active:
            self.voice_client.update_transmitter(self.com2_transmitter)

    def start(self):
        self.voice_client.add_transmitter(self.com1_transmitter, False, False)
        self.voice_client.add_transmitter(self.com2_transmitter, False, False)
        self.thread_exit.clear()
        Thread(target=self._receive_frequency, daemon=True).start()

    def stop(self):
        self.thread_exit.set()

    def _receive_frequency(self):
        err_count = 0
        while not self.thread_exit.is_set():
            res = self.fsuipc_client.get_frequency()
            if res.requestStatus:
                self.update_com_info(res.frequency[0] // 1000,
                                     res.frequency[2] // 1000,
                                     (res.frequencyFlag & 0x80) != 0x80,
                                     (res.frequencyFlag & 0x40) != 0x40)
            else:
                logger.error(f"Error while receiving frequency from FSUIPC: {res.errMessage}")
                err_count += 1
            if err_count >= 3:
                logger.error(f"Too many error received from FSUIPC: {err_count}, disconnecting")
            sleep(1)

    def update_com_info(self, com1_freq: int, com2_freq: int, com1_rx: bool, com2_rx: bool):
        if self.com1_transmitter.receive_flag != com1_rx:
            self.com1_transmitter.receive_flag = com1_rx
            self.button_com1_rx.active = com1_rx

        if self.com1_transmitter.frequency != com1_freq:
            self.label_com1_freq.setText(f"{com1_freq / 1000:.3f}")
            if self.button_com1_tx.active:
                self.com1_transmitter.frequency = com1_freq

        if self.com2_transmitter.receive_flag != com2_rx:
            self.com2_transmitter.receive_flag = com2_rx
            self.button_com2_rx.active = com2_rx

        if self.com2_transmitter.frequency != com2_freq:
            self.label_com2_freq.setText(f"{com2_freq / 1000:.3f}")
            if self.button_com2_tx.active:
                self.com2_transmitter.frequency = com2_freq
