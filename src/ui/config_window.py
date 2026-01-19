#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from PySide6.QtWidgets import QWidget
from loguru import logger

from .form import Ui_ConfigWindow
from src.config import config, config_manager
from src.signal import AudioClientSignals
from src.utils import get_device_info, get_host_api_info


class ConfigWindow(QWidget, Ui_ConfigWindow):
    def __init__(self, audio_signal: AudioClientSignals):
        super().__init__()
        self.setupUi(self)
        config_manager.register_save_callback(self.update_config_data)

        self.audio_signal = audio_signal

        self._audio_drivers = get_host_api_info()
        self._audio_inputs: dict[str, int] = {}
        self._audio_outputs: dict[str, int] = {}
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

        self.button_cancel.clicked.connect(self.cancel)
        self.button_apply.clicked.connect(self.apply)
        self.button_ok.clicked.connect(self.save)

        self.button_ptt.select_message = "按下ESC退出"

    def audio_input_device_change(self, value: str):
        if not value:
            return
        logger.trace(f"Audio input device change: {value}")
        self.audio_signal.audio_input_device_change.emit(self._audio_inputs.get(value, -1))

    def audio_output_device_change(self, value: str):
        if not value:
            return
        logger.trace(f"Audio output device change: {value}")
        self.audio_signal.audio_output_device_change.emit(self._audio_outputs.get(value, -1))

    def audio_device_update(self, driver_name: str):
        logger.trace(f"Audio device driver update to: {driver_name}")
        driver_id = self._audio_drivers.get(driver_name, -1)
        if driver_id == -1:
            for name in self._audio_drivers:
                if "WASAPI" in name:
                    driver_id = self._audio_drivers[name]
            if driver_id == -1:
                driver_id = 0
        self._audio_inputs, self._audio_outputs = get_device_info(driver_id)

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

    def update_config_data(self) -> bool:
        self.label_config_version_2.setText(config.version)
        self.combo_box_log_level.setCurrentText(config.log.level.upper())

        self.line_edit_account.setText(config.account.username)
        self.line_edit_password.setText(config.account.password)

        self.line_edit_server_address.setText(config.server.voice_endpoint)
        self.line_edit_tcp_port.setText(str(config.server.voice_tcp_port))
        self.line_edit_udp_port.setText(str(config.server.voice_udp_port))

        self.combo_box_audio_driver.setCurrentText(config.audio.api_driver)
        self.combo_box_audio_input.setCurrentText(config.audio.input_device)
        self.combo_box_audio_output.setCurrentText(config.audio.output_device)
        self.button_ptt.selected_key = config.audio.ptt_key

        return True

    def save(self):
        self.apply()
        self.hide()

    def apply(self):
        config.log.level = self.combo_box_log_level.currentText().upper()

        config.account.username = self.line_edit_account.text()
        config.account.password = self.line_edit_password.text()

        config.server.voice_endpoint = self.line_edit_server_address.text()
        config.server.voice_tcp_port = int(self.line_edit_tcp_port.text())
        config.server.voice_udp_port = int(self.line_edit_udp_port.text())

        config.audio.api_driver = self.combo_box_audio_driver.currentText()
        config.audio.input_device = self.combo_box_audio_input.currentText()
        config.audio.output_device = self.combo_box_audio_output.currentText()
        config.audio.ptt_key = self.button_ptt.selected_key

        config_manager.save()

    def cancel(self):
        self.hide()
