#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
from PySide6.QtCore import Qt, QTimer
from loguru import logger

from src.config import config, config_manager
from src.model import ConnectionState, DeviceInfo
from src.signal import AudioClientSignals
from src.utils import get_device_info, get_host_api_info
from .component.frameless_widget import FramelessWidget
from .form import Ui_ConfigWindow


class ConfigWindow(FramelessWidget, Ui_ConfigWindow):
    def __init__(self, signals: AudioClientSignals):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        config_manager.register_save_callback(self.update_config_data)

        self.signals = signals

        self._audio_drivers = get_host_api_info()
        self._audio_inputs: dict[str, DeviceInfo] = {}
        self._audio_outputs: dict[str, DeviceInfo] = {}
        self.combo_box_audio_driver.addItem("自动")
        for driver in self._audio_drivers:
            self.combo_box_audio_driver.addItem(driver)

        self.combo_box_audio_driver.currentTextChanged.connect(self.audio_device_update)
        self.audio_device_update(self.combo_box_audio_driver.currentText())
        self.update_config_data()
        self.combo_box_audio_input.currentTextChanged.connect(self.audio_input_device_change)
        self.audio_input_device_change(self.combo_box_audio_input.currentText())
        self.combo_box_audio_output.currentTextChanged.connect(self.audio_output_device_change)
        self.audio_output_device_change(self.combo_box_audio_output.currentText())
        self.combo_box_audio_output_speaker.currentTextChanged.connect(self.audio_output_speaker_device_change)
        self.audio_output_speaker_device_change(self.combo_box_audio_output_speaker.currentText())

        self.microphone_gain.sliderMoved.connect(self.microphone_gain_change)
        self.button_test_headphone.clicked.connect(self._test_headphone)
        self.button_test_speaker.clicked.connect(self._test_speaker)
        self.button_test_conflict.clicked.connect(self._test_conflict)

        self.button_cancel.clicked.connect(self.cancel)
        self.button_apply.clicked.connect(self.apply)
        self.button_ok.clicked.connect(self.save)

        self.button_ptt.select_message = "按下ESC退出"

        self.ptt_sound.sliderMoved.connect(self.ptt_volume_change)
        self.ptt_press_freq.valueChanged.connect(self.ptt_press_freq_change)
        self.ptt_release_freq.valueChanged.connect(self.ptt_release_freq_change)
        self.conflict_volume.sliderMoved.connect(self.conflict_volume_change)
        self.signals.connection_state_changed.connect(
            self.handle_connect_status_change, Qt.ConnectionType.QueuedConnection
        )

    def _any_test_active(self) -> bool:
        return (
                self.button_test_headphone.active
                or self.button_test_speaker.active
                or self.button_test_conflict.active
        )

    def _update_test_buttons_state(self) -> None:
        any_test = self._any_test_active()
        self.button_ok.setEnabled(not any_test)
        self.button_apply.setEnabled(not any_test)
        self.button_cancel.setEnabled(not any_test)

    def _test_headphone(self) -> None:
        active = self.button_test_headphone.active
        if active:
            self.button_test_speaker.active = False
            self.button_test_conflict.active = False
        self.signals.test_audio_device.emit(active, "headphone")
        self._update_test_buttons_state()

    def _test_speaker(self) -> None:
        active = self.button_test_speaker.active
        if active:
            self.button_test_headphone.active = False
            self.button_test_conflict.active = False
        self.signals.test_audio_device.emit(active, "speaker")
        self._update_test_buttons_state()

    def _test_conflict(self) -> None:
        active = self.button_test_conflict.active
        if active:
            self.button_test_headphone.active = False
            self.button_test_speaker.active = False
        self.signals.test_audio_device.emit(active, "conflict")
        self._update_test_buttons_state()

    def microphone_gain_change(self, value: int):
        self.label_microphone_gain.setText(f"{value}dB")
        self.signals.microphone_gain_changed.emit(value)

    def audio_input_device_change(self, value: str):
        if not value:
            return
        logger.trace(f"Audio input device change: {value}")
        self.signals.audio_input_device_change.emit(self._audio_inputs.get(value, None))

    def audio_output_device_change(self, value: str):
        if not value:
            return
        logger.trace(f"Audio output (headphone) device change: {value}")
        self.signals.audio_output_device_change.emit(self._audio_outputs.get(value, None))

    def audio_output_speaker_device_change(self, value: str):
        if not value:
            return
        logger.trace(f"Audio output (speaker) device change: {value}")
        self.signals.audio_output_device_speaker_change.emit(self._audio_outputs.get(value, None))

    def audio_device_update(self, driver_name: str):
        logger.trace(f"Audio device driver update to: {driver_name}")
        driver = self._audio_drivers.get(driver_name, None)
        if driver is None:
            logger.warning(f"Audio device driver not found: {driver_name}")
            for name in self._audio_drivers:
                if "WASAPI" in name:
                    driver = self._audio_drivers[name]
                    logger.info(f"Default audio device driver found: {name}")
            if driver is None:
                logger.error(f"No default audio device driver found")
                driver = self._audio_drivers[list(self._audio_drivers.keys())[0]]
        self._audio_inputs, self._audio_outputs = get_device_info(driver.index)

        self.combo_box_audio_input.clear()
        self.combo_box_audio_input.addItem("默认")
        for input_device in self._audio_inputs:
            self.combo_box_audio_input.addItem(input_device)
        self.combo_box_audio_input.setCurrentIndex(0)

        self.combo_box_audio_output.clear()
        self.combo_box_audio_output.addItem("默认")
        for output_device in self._audio_outputs:
            self.combo_box_audio_output.addItem(output_device)
        self.combo_box_audio_output.setCurrentIndex(0)
        self.combo_box_audio_output_speaker.clear()
        self.combo_box_audio_output_speaker.addItem("默认")
        for output_device in self._audio_outputs:
            self.combo_box_audio_output_speaker.addItem(output_device)
        self.combo_box_audio_output_speaker.setCurrentIndex(0)

    def ptt_volume_change(self, value: int):
        self.ptt_sound_value.setText(f"{value / 100:.0%}")
        self.signals.ptt_volume_changed.emit(value / 100)

    def ptt_press_freq_change(self, value: float):
        self.signals.ptt_press_freq_changed.emit(value)

    def ptt_release_freq_change(self, value: float):
        self.signals.ptt_release_freq_changed.emit(value)

    def conflict_volume_change(self, value: int):
        self.conflict_volume_v.setText(f"{value}%")
        self.signals.conflict_volume_changed.emit(value / 100)

    def update_config_data(self) -> bool:
        self.label_config_version_2.setText(config.version)
        self.combo_box_log_level.setCurrentText(config.log.level.upper())

        self.line_edit_account.setText(config.account.username)
        self.line_edit_password.setText(config.account.password)

        self.combo_box_audio_driver.setCurrentText(config.audio.api_driver)
        self.combo_box_audio_input.setCurrentText(config.audio.input_device)
        self.combo_box_audio_output.setCurrentText(config.audio.output_device)
        self.combo_box_audio_output_speaker.setCurrentText(config.audio.output_device_speaker)
        self.button_ptt.selected_key = config.audio.ptt_key
        self.label_microphone_gain.setText(f"{config.audio.microphone_gain}dB")
        self.microphone_gain.setValue(config.audio.microphone_gain)
        self.ptt_press_freq.setValue(config.audio.ptt_press_freq)
        self.ptt_release_freq.setValue(config.audio.ptt_release_freq)
        self.ptt_sound.setValue(int(config.audio.ptt_volume * 100))
        self.ptt_sound_value.setText(f"{config.audio.ptt_volume:.0%}")
        self.conflict_volume.setValue(int(config.audio.conflict_volume * 100))
        self.conflict_volume_v.setText(f"{config.audio.conflict_volume * 100:.0f}%")

        return True

    def save(self):
        self.apply()
        self.hide()

    def apply(self):
        config.log.level = self.combo_box_log_level.currentText().upper()

        config.account.username = self.line_edit_account.text()
        config.account.password = self.line_edit_password.text()

        config.audio.api_driver = self.combo_box_audio_driver.currentText()
        config.audio.input_device = self.combo_box_audio_input.currentText()
        config.audio.output_device = self.combo_box_audio_output.currentText()
        config.audio.output_device_speaker = self.combo_box_audio_output_speaker.currentText()
        config.audio.ptt_key = self.button_ptt.selected_key
        config.audio.microphone_gain = self.microphone_gain.value()
        config.audio.ptt_press_freq = self.ptt_press_freq.value()
        config.audio.ptt_release_freq = self.ptt_release_freq.value()
        config.audio.ptt_volume = self.ptt_sound.value() / 100
        config.audio.conflict_volume = self.conflict_volume.value() / 100

        config_manager.save()

    def cancel(self):
        self.hide()
        self.button_test_conflict.active = False
        self.signals.test_audio_device.emit(False, "")
        self.signals.microphone_gain_changed.emit(config.audio.microphone_gain)
        self.signals.audio_input_device_change.emit(self._audio_inputs.get(config.audio.input_device, None))
        self.signals.audio_output_device_change.emit(self._audio_outputs.get(config.audio.output_device, None))
        self.signals.audio_output_device_speaker_change.emit(
            self._audio_outputs.get(config.audio.output_device_speaker, None))
        self.signals.ptt_press_freq_changed.emit(config.audio.ptt_press_freq)
        self.signals.ptt_release_freq_changed.emit(config.audio.ptt_release_freq)
        self.signals.ptt_volume_changed.emit(config.audio.ptt_volume)
        self.signals.conflict_volume_changed.emit(config.audio.conflict_volume)

    def handle_connect_status_change(self, status: ConnectionState) -> None:
        match status:
            case ConnectionState.CONNECTING:
                self.button_test_headphone.active = False
                self.button_test_speaker.active = False
                self.button_test_conflict.active = False
                self.button_test_headphone.setEnabled(False)
                self.button_test_speaker.setEnabled(False)
                self.button_test_conflict.setEnabled(False)
                self.signals.test_audio_device.emit(False, "")
                self.button_ok.setEnabled(True)
                self.button_apply.setEnabled(True)
                self.button_cancel.setEnabled(True)
            case ConnectionState.DISCONNECTED:
                self.button_test_headphone.setEnabled(True)
                self.button_test_speaker.setEnabled(True)
                self.button_test_conflict.setEnabled(True)
