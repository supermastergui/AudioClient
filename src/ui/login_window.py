#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from urllib.parse import urljoin

from PySide6.QtWidgets import QMessageBox, QWidget
from loguru import logger

from .form import Ui_LoginWindow
from src.config import config, config_manager
from src.utils import http
from src.signal import AudioClientSignals
from src.core import VoiceClient
from src.utils import get_line_edit_data
from ..model import UserLoginRequest, UserLoginResponse


class LoginWindow(QWidget, Ui_LoginWindow):
    def __init__(self, voice_client: VoiceClient, signals: AudioClientSignals):
        super().__init__()
        self.setupUi(self)
        self.button_login.clicked.connect(self.login)
        self.check_box_remember_me.clicked.connect(self.remember_me_change)
        config_manager.on_config_save(self.update_config_data)
        self.update_config_data()
        self.voice_client = voice_client
        self.signals = signals
        self.button_settings.clicked.connect(lambda: signals.show_config_windows.emit())

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
        logger.trace("Logging in application")
        username = get_line_edit_data(self.line_edit_account, str)
        password = get_line_edit_data(self.line_edit_password, str)
        if username is None or password is None:
            logger.error(f"Account or password not provided")
            QMessageBox.critical(self, "参数错误", "请输入账号和密码")
            return

        response = http.client.post(urljoin(config.server.api_endpoint, "/api/users/sessions"),
                                    json=UserLoginRequest(username=username, password=password).model_dump())

        if response.status_code != 200:
            logger.error(f"Login failed with status code {response.status_code}")
            try:
                QMessageBox.critical(self, "登陆失败", response.json().get("message"))
            except Exception as _:
                QMessageBox.critical(self, "登陆失败", "发生未知错误")
            return

        data = UserLoginResponse.model_validate(response.json()).data

        self.voice_client.client_info.cid = data.user.cid
        self.voice_client.client_info.jwt_token = data.token
        self.voice_client.client_info.flush_token = data.flush_token
        self.voice_client.client_info.user = data.user

        logger.success(f"Logged in successfully")
        logger.trace(f"Logged in as {data.user.username}({data.user.cid:04}), token={data.token}")

        self.remember_me_change(self.check_box_remember_me.isChecked())
        self.signals.login_success.emit()
