from urllib.parse import urljoin

from PySide6.QtWidgets import QMessageBox, QWidget
from loguru import logger

from .form import Ui_LoginWindow
from src.config import config
from src.utils import http
from src.signal import Signals
from src.core import VoiceClient
from src.utils import get_line_edit_data


class LoginWindow(QWidget, Ui_LoginWindow):
    def __init__(self, voice_client: VoiceClient, signals: Signals):
        super().__init__()
        self.setupUi(self)
        self.button_login.clicked.connect(self.login)
        self.check_box_remember_me.clicked.connect(self.remember_me_change)
        config.add_config_save_callback(self.update_config_data)
        self.update_config_data()
        self.voice_client = voice_client
        self.signals = signals
        self.button_settings.clicked.connect(lambda: signals.show_config_windows.emit())

    def update_config_data(self):
        if config.remember_me:
            self.check_box_remember_me.setChecked(True)
            self.line_edit_account.setText(config.account)
            self.line_edit_password.setText(config.password)

    def remember_me_change(self, value: bool) -> None:
        if value:
            config.account = self.line_edit_account.text()
            config.password = self.line_edit_password.text()
            config.remember_me = True
            config.save_config()
        else:
            config.remember_me = False
            config.save_config()

    def login(self) -> None:
        logger.trace("Logging in application")
        account = get_line_edit_data(self.line_edit_account, str)
        password = get_line_edit_data(self.line_edit_password, str)
        if account is None or password is None:
            logger.error(f"Account or password not provided")
            QMessageBox.critical(self, "参数错误", "请输入账号和密码")
            return

        response = http.client.post(urljoin(config.base_url, "/api/users/sessions"), json={
            "username": account,
            "password": password
        })

        if response.status_code != 200:
            logger.error(f"Login failed with status code {response.status_code}")
            try:
                QMessageBox.critical(self, "登陆失败", response.json().get("message"))
            except Exception as _:
                QMessageBox.critical(self, "登陆失败", "发生未知错误")
            return

        data = response.json()["data"]

        self.voice_client.client_info.cid = data["user"]["cid"]
        self.voice_client.client_info.jwt_token = data["token"]

        logger.success(f"Logged in successfully")
        logger.trace(f"Logged in as {account}, "
                     f"cid={self.voice_client.client_info.cid}, "
                     f"token={self.voice_client.client_info.jwt_token}")

        self.remember_me_change(self.check_box_remember_me.isChecked())
        self.signals.login_success.emit()
