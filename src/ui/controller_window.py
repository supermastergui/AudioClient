#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from src.core import OutputTarget, Transmitter, VoiceClient
from src.model import ConnectionState
from src.signal import AudioClientSignals
from src.utils import clear_error, show_error
from .form import Ui_ControllerWindow
from .sub_window import SubWindow


class ControllerWindow(QWidget, Ui_ControllerWindow):
    def __init__(self, signals: AudioClientSignals, voice_client: VoiceClient):
        super().__init__()
        self.setupUi(self)

        self.voice_client = voice_client
        self.signals = signals
        self._frequency = -1
        self._main_transmitter = Transmitter(0, 0)
        self._unicom_transmitter = Transmitter(122800, 1)
        self._emer_transmitter = Transmitter(121500, 2)
        self._custom_transmitter = Transmitter(0, 3)

        self.button_main_freq_tx.clicked.connect(self.main_freq_tx_click)
        self.button_main_freq_rx.clicked.connect(self.main_freq_rx_click)
        self.button_unicom_freq_tx.clicked.connect(self.unicom_freq_tx_click)
        self.button_unicom_freq_rx.clicked.connect(self.unicom_freq_rx_click)
        self.button_emer_freq_tx.clicked.connect(self.emer_freq_tx_click)
        self.button_emer_freq_rx.clicked.connect(self.emer_freq_rx_click)
        self.button_freq_tx.clicked.connect(self.freq_tx_click)
        self.button_freq_rx.clicked.connect(self.freq_rx_click)
        # 以下信号可能在网络线程中 emit，用 QueuedConnection 保证槽在主线程执行
        self.voice_client.signals.connection_state_changed.connect(
            self.connect_state_changed, Qt.ConnectionType.QueuedConnection
        )
        self.voice_client.signals.update_current_frequency.connect(
            self.set_current_frequency, Qt.ConnectionType.QueuedConnection
        )
        self.line_edit_freq.editingFinished.connect(self.decode_frequency)
        self.button_mute.clicked.connect(self.mute_all)
        self.voice_volume.sliderMoved.connect(self.voice_volume_move)
        self.main_voice_volume.sliderMoved.connect(self.main_voice_volume_move)
        self.unicom_voice_volume.sliderMoved.connect(self.unicom_voice_volume_move)
        self.emer_voice_volume.sliderMoved.connect(self.emer_voice_volume_move)
        self.custom_voice_volume.sliderMoved.connect(self.custom_voice_volume_move)

        self.sub_window = SubWindow(signals)
        self.button_small_window.clicked.connect(lambda: self.signals.show_small_window.emit())

        self.button_main_speaker.setEnabled(False)
        self.button_emer_speaker.setEnabled(False)
        self.button_unicom_speaker.setEnabled(False)
        self.button_freq_speaker.setEnabled(False)
        self.button_main_speaker.clicked.connect(
            lambda: self._on_output_target_change(self._main_transmitter, self.button_main_speaker.active)
        )
        self.button_emer_speaker.clicked.connect(
            lambda: self._on_output_target_change(self._emer_transmitter, self.button_emer_speaker.active)
        )
        self.button_unicom_speaker.clicked.connect(
            lambda: self._on_output_target_change(self._unicom_transmitter, self.button_unicom_speaker.active)
        )
        self.button_freq_speaker.clicked.connect(
            lambda: self._on_output_target_change(self._custom_transmitter, self.button_freq_speaker.active)
        )

    def _on_output_target_change(self, transmitter: Transmitter, speaker: bool) -> None:
        transmitter.output_target = OutputTarget.Speaker if speaker else OutputTarget.Headphone
        if self.voice_client.client_ready:
            self.voice_client.set_transmitter_output_target(transmitter)

    def voice_volume_move(self, volume: int):
        if self.main_voice_volume.value() > volume:
            self.main_voice_volume.setValue(volume)
            self.label_main_voice_volume.setText(f"{self.main_voice_volume.value() / 50:.0%}")
        if self.unicom_voice_volume.value() > volume:
            self.unicom_voice_volume.setValue(volume)
            self.label_unicom_voice_volume.setText(f"{self.unicom_voice_volume.value() / 50:.0%}")
        if self.emer_voice_volume.value() > volume:
            self.emer_voice_volume.setValue(volume)
            self.label_emer_voice_volume.setText(f"{self.emer_voice_volume.value() / 50:.0%}")
        if self.custom_voice_volume.value() > volume:
            self.custom_voice_volume.setValue(volume)
            self.label_custom_voice_volume.setText(f"{self.custom_voice_volume.value() / 50:.0%}")
        self.label_voice_volume.setText(f"{volume / 50:.0%}")
        self._main_transmitter.volume = self.main_voice_volume.value() * volume / 2500
        self._unicom_transmitter.volume = self.unicom_voice_volume.value() * volume / 2500
        self._emer_transmitter.volume = self.emer_voice_volume.value() * volume / 2500
        self._custom_transmitter.volume = self.custom_voice_volume.value() * volume / 2500

    def main_voice_volume_move(self, volume: int):
        if volume > self.voice_volume.value():
            volume = self.voice_volume.value()
            self.main_voice_volume.setValue(volume)
        self._main_transmitter.volume = volume * self.voice_volume.value() / 2500
        self.label_main_voice_volume.setText(f"{volume / 50:.0%}")

    def unicom_voice_volume_move(self, volume: int):
        if volume > self.voice_volume.value():
            volume = self.voice_volume.value()
            self.unicom_voice_volume.setValue(volume)
        self._unicom_transmitter.volume = volume * self.voice_volume.value() / 2500
        self.label_unicom_voice_volume.setText(f"{volume / 50:.0%}")

    def emer_voice_volume_move(self, volume: int):
        if volume > self.voice_volume.value():
            volume = self.voice_volume.value()
            self.emer_voice_volume.setValue(volume)
        self._emer_transmitter.volume = volume * self.voice_volume.value() / 2500
        self.label_emer_voice_volume.setText(f"{volume / 50:.0%}")

    def custom_voice_volume_move(self, volume: int):
        if volume > self.voice_volume.value():
            volume = self.voice_volume.value()
            self.custom_voice_volume.setValue(volume)
        self._custom_transmitter.volume = volume * self.voice_volume.value() / 2500
        self.label_custom_voice_volume.setText(f"{volume / 50:.0%}")

    def mute_all(self):
        if self.button_mute.active:
            self.voice_volume.setEnabled(False)
            self.main_voice_volume.setEnabled(False)
            self.unicom_voice_volume.setEnabled(False)
            self.emer_voice_volume.setEnabled(False)
            self.custom_voice_volume.setEnabled(False)
            self.label_voice_volume.setText("0%")
            self._main_transmitter.volume = 0
            self.label_main_voice_volume.setText("0%")
            self._unicom_transmitter.volume = 0
            self.label_unicom_voice_volume.setText("0%")
            self._emer_transmitter.volume = 0
            self.label_emer_voice_volume.setText("0%")
            self._custom_transmitter.volume = 0
            self.label_custom_voice_volume.setText("0%")
        else:
            self.voice_volume.setEnabled(True)
            self.main_voice_volume.setEnabled(True)
            self.unicom_voice_volume.setEnabled(True)
            self.emer_voice_volume.setEnabled(True)
            self.custom_voice_volume.setEnabled(self._frequency != -1)
            self.label_voice_volume.setText(f"{self.voice_volume.value() / 50:.0%}")
            self._main_transmitter.volume = self.main_voice_volume.value() * self.voice_volume.value() / 2500
            self.label_main_voice_volume.setText(f"{self.main_voice_volume.value() / 50:.0%}")
            self._unicom_transmitter.volume = self.unicom_voice_volume.value() * self.voice_volume.value() / 2500
            self.label_unicom_voice_volume.setText(f"{self.unicom_voice_volume.value() / 50:.0%}")
            self._emer_transmitter.volume = self.emer_voice_volume.value() * self.voice_volume.value() / 2500
            self.label_emer_voice_volume.setText(f"{self.emer_voice_volume.value() / 50:.0%}")
            self._custom_transmitter.volume = self.custom_voice_volume.value() * self.voice_volume.value() / 2500
            self.label_custom_voice_volume.setText(f"{self.custom_voice_volume.value() / 50:.0%}")

    def set_current_frequency(self, frequency: int):
        freq = f"{frequency / 1000:.3f}" if frequency != 0 else "---.---"
        self.label_current_freq_v.setText(freq)
        self.sub_window.label_current_freq_v.setText(freq)

    def decode_frequency(self):
        try:
            frequency = int(float(self.line_edit_freq.text()) * 1000)
        except ValueError:
            frequency = 0
        if frequency < 3000 or frequency > 200000:
            show_error(self.line_edit_freq)
            self._frequency = -1
            self.button_freq_rx.active = False
            self.button_freq_tx.active = False
            self.button_freq_speaker.active = False
            self.button_freq_rx.setEnabled(False)
            self.button_freq_tx.setEnabled(False)
            self.button_freq_speaker.setEnabled(False)
            self.custom_voice_volume.setEnabled(False)
            return
        clear_error(self.line_edit_freq)
        self.button_freq_rx.setEnabled(True)
        self.button_freq_tx.setEnabled(True)
        self.button_freq_speaker.setEnabled(self.button_freq_rx.active)
        if not self.button_mute.active:
            self.custom_voice_volume.setEnabled(True)
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
        self._custom_transmitter.send_flag = self.button_freq_tx.active
        self._custom_transmitter.receive_flag = self.button_freq_rx.active
        self.button_freq_speaker.setEnabled(self.button_freq_rx.active)
        self.voice_client.update_transmitter(self._custom_transmitter)

    def main_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_emer_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        self._main_transmitter.send_flag = self.button_main_freq_tx.active
        self.voice_client.update_transmitter(self._main_transmitter)

    def main_freq_rx_click(self):
        self._main_transmitter.send_flag = self.button_main_freq_tx.active
        self._main_transmitter.receive_flag = self.button_main_freq_rx.active
        self.button_main_speaker.setEnabled(self.button_main_freq_rx.active)
        self.voice_client.update_transmitter(self._main_transmitter)

    def unicom_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_emer_freq_tx.active = False
        self.button_main_freq_tx.active = False
        self._unicom_transmitter.send_flag = self.button_unicom_freq_tx.active
        self.button_main_speaker.setEnabled(self.button_main_freq_rx.active)
        self.voice_client.update_transmitter(self._unicom_transmitter)

    def unicom_freq_rx_click(self):
        self._unicom_transmitter.send_flag = self.button_unicom_freq_tx.active
        self._unicom_transmitter.receive_flag = self.button_unicom_freq_rx.active
        self.button_unicom_speaker.setEnabled(self.button_unicom_freq_rx.active)
        self.voice_client.update_transmitter(self._unicom_transmitter)

    def emer_freq_tx_click(self):
        self.button_freq_tx.active = False
        self.button_main_freq_tx.active = False
        self.button_unicom_freq_tx.active = False
        self._emer_transmitter.send_flag = self.button_emer_freq_tx.active
        self.voice_client.update_transmitter(self._emer_transmitter)

    def emer_freq_rx_click(self):
        self._emer_transmitter.send_flag = self.button_emer_freq_tx.active
        self._emer_transmitter.receive_flag = self.button_emer_freq_rx.active
        self.button_emer_speaker.setEnabled(self.button_emer_freq_rx.active)
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

        self.button_freq_speaker.active = False
        self.button_freq_tx.setEnabled(False)
        self.button_freq_rx.setEnabled(False)
        self.button_freq_speaker.setEnabled(False)

    def connect_state_changed(self, state: ConnectionState):
        if not self.voice_client.client_info.is_atc:
            return
        if state == ConnectionState.READY:
            self.clear()
            self._main_transmitter.frequency = self.voice_client.client_info.main_frequency
            self.voice_client.add_transmitter(self._main_transmitter)
            self.signals.show_log_message.emit("ControllerWindow", "INFO",
                                               f"主频率注册成功，{self._main_transmitter.output_target}")
            self.voice_client.add_transmitter(self._unicom_transmitter)
            self.signals.show_log_message.emit("ControllerWindow", "INFO",
                                               f"UNICOM注册成功，{self._unicom_transmitter.output_target}")
            self.voice_client.add_transmitter(self._emer_transmitter)
            self.signals.show_log_message.emit("ControllerWindow", "INFO",
                                               f"紧急频率注册成功，{self._emer_transmitter.output_target}")
            self.voice_client.add_transmitter(self._custom_transmitter)
            self.signals.show_log_message.emit("ControllerWindow", "INFO",
                                               f"自定义频率注册成功，{self._unicom_transmitter.output_target}")
            self.label_main_freq_v.setText(f"{self.voice_client.client_info.main_frequency / 1000:.3f}")
        elif state == ConnectionState.DISCONNECTED:
            self.clear()
