#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
from json import JSONDecodeError
from urllib.parse import urljoin

from PySide6.QtWidgets import QMessageBox, QWidget
from loguru import logger

from src.config import config, config_manager
from src.core import VoiceClient
from src.model import UserLoginRequest, UserLoginResponse
from src.signal import AudioClientSignals
from src.utils import get_line_edit_data, http
from .form import Ui_LoginWindow


class LoginWindow(QWidget, Ui_LoginWindow):
    def __init__(self, signals: AudioClientSignals, voice_client: VoiceClient):
        super().__init__()
        self.setupUi(self)

        self.voice_client = voice_client
        self.signals = signals

        self.button_login.clicked.connect(self.login)
        self.check_box_remember_me.clicked.connect(self.remember_me_change)
        self.button_settings.clicked.connect(lambda: signals.show_config_windows.emit())

        config_manager.on_config_save(self.update_config_data)
        self.update_config_data()

    def update_config_data(self) -> bool:
        if config.account.remember_me:
            self.check_box_remember_me.setChecked(True)
            self.line_edit_account.setText(config.account.username)
            self.line_edit_password.setText(config.account.password)
        return True

    def remember_me_change(self, value: bool) -> None:
        if value:
            config.account.username = self.line_edit_account.text()
            config.account.password = self.line_edit_password.text()
            config.account.remember_me = True
            config_manager.save()
        else:
            config.account.username = ""
            config.account.password = ""
            config.account.remember_me = False
            config_manager.save()

    def login(self) -> None:
        logger.debug("LoginWindow > logging in")
        username = get_line_edit_data(self.line_edit_account, str)
        password = get_line_edit_data(self.line_edit_password, str)
        if username is None or password is None:
            logger.error(f"LoginWindow > account or password not provided")
            QMessageBox.critical(self, "参数错误", "请输入账号和密码")
            return

        response = http.client.post(urljoin(config.server.api_endpoint, "/api/users/sessions"),
                                    json=UserLoginRequest(username=username, password=password).model_dump())

        if response.status_code != 200:
            logger.error(f"LoginWindow > login failed with status code {response.status_code}")
            try:
                QMessageBox.critical(self, "登陆失败", response.json().get("message", "发生未知错误"))
            except JSONDecodeError:
                QMessageBox.critical(self, "登陆失败", f"未知错误，错误代码: {response.status_code}")
            return

        data = UserLoginResponse.model_validate_json(response.content).data

        self.voice_client.update_client_info(data)

        logger.success(f"LoginWindow > logged in successfully, user: {data.user.username}({data.user.cid:04})")

        self.remember_me_change(self.check_box_remember_me.isChecked())
        self.signals.login_success.emit()
