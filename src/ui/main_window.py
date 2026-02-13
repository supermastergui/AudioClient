#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from loguru import logger

from src.config import config, config_manager
from src.constants import app_name, app_title, session_refresh_interval_minutes
from src.core import VoiceClient
from src.model import ConnectionState
from src.signal import AudioClientSignals, JoystickSignals, KeyBoardSignals, MouseSignals
from src.thread import JoystickListenerThread, KeyboardListenerThread, MouseListenerThread
from src.utils import http
from src.utils.auth import refresh_session
from .component import PTTButton
from .config_window import ConfigWindow
from .connect_window import ConnectWindow
from .form import Ui_MainWindow
from .loading_window import LoadingWindow
from .login_window import LoginWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, signals: AudioClientSignals, mouse_signals: MouseSignals,
                 keyboard_signals: KeyBoardSignals, joystick_signals: JoystickSignals) -> None:
        super().__init__()
        self.setupUi(self)
        self.resize(300, 300)
        self.setMinimumSize(300, 300)
        self.setWindowTitle(app_title)
        self.menubar.setVisible(False)

        self.voice_client: Optional[VoiceClient] = None
        self.keyboard_listener: Optional[KeyboardListenerThread] = None
        self.mouse_listener: Optional[MouseListenerThread] = None
        self.joystick_listener: Optional[JoystickListenerThread] = None
        self.connect_window: Optional[ConnectWindow] = None
        self.login: Optional[LoginWindow] = None
        self.config: Optional[ConfigWindow] = None
        self.ptt_button: Optional[PTTButton] = None
        self._refresh_timer = QTimer()

        self.loading = LoadingWindow()
        self.loading.setObjectName(u"loading")
        self.windows.addWidget(self.loading)
        self.windows.setCurrentIndex(0)

        self.signals = signals
        self.mouse_signals = mouse_signals
        self.keyboard_signals = keyboard_signals
        self.joystick_signals = joystick_signals

        config_manager.register_save_callback(self.config_update)

        http.initialize()
        # client_initialized 在 threading.Thread 中 emit，槽会大量更新 UI，必须 QueuedConnection
        http.client_initialized.connect(
            self.initialize_complete, Qt.ConnectionType.QueuedConnection
        )
        self.action_settings.triggered.connect(self.show_config_window)
        self.action_about.triggered.connect(self.show_about)
        self.action_about_qt.triggered.connect(self.show_about_qt)
        signals.show_config_windows.connect(self.show_config_window)
        signals.logout_request.connect(self.logout_request)
        signals.resize_window.connect(self.resize_window)
        self._refresh_timer.timeout.connect(self._do_refresh)

    def logout_request(self) -> None:
        self._refresh_timer.stop()
        if self.voice_client is not None:
            self.voice_client.client_info.reset()
        self.windows.setCurrentIndex(1)
        self.resize_window(600, 600, True)

    def _do_refresh(self) -> None:
        if self.voice_client is None:
            return
        flush_token = self.voice_client.client_info.flush_token
        if not flush_token:
            return
        data = refresh_session(flush_token)
        if data is None:
            return
        self.voice_client.update_client_info(data)
        logger.debug("MainWindow > session refreshed")

    def login_success(self) -> None:
        self.resize_window(600, 300, True)
        self.windows.setCurrentIndex(2)
        if session_refresh_interval_minutes > 0:
            self._refresh_timer.start(session_refresh_interval_minutes * 60 * 1000)

    def config_update(self) -> bool:
        if self.ptt_button is None:
            return False
        self.ptt_button.set_target_key(config.audio.ptt_key)
        return True

    def initialize_complete(self) -> None:
        self.setMinimumSize(0, 0)

        self.voice_client = VoiceClient(self.signals)

        self.login = LoginWindow(self.signals, self.voice_client)
        self.login.setObjectName(u"login")
        self.windows.addWidget(self.login)

        self.connect_window = ConnectWindow(self.signals, self.voice_client)
        self.connect_window.setObjectName(u"connect")
        self.signals.show_small_window.connect(self.hide)
        self.signals.show_full_window.connect(self.show)
        self.windows.addWidget(self.connect_window)

        self.config = ConfigWindow(self.signals)
        self.config.setObjectName(u"config")

        self.signals.login_success.connect(self.login_success)

        self.mouse_listener = MouseListenerThread(self.mouse_signals)
        self.keyboard_listener = KeyboardListenerThread(self.keyboard_signals)
        self.joystick_listener = JoystickListenerThread(self.joystick_signals)

        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.joystick_listener.start()

        self.config.button_ptt.mouse_signal = self.mouse_signals
        self.config.button_ptt.keyboard_signal = self.keyboard_signals
        self.config.button_ptt.joystick_signal = self.joystick_signals

        self.ptt_button = PTTButton()
        self.config_update()
        # 以下信号在监听线程 (QThread) 中 emit，用 QueuedConnection 保证槽在主线程执行
        self.mouse_signals.mouse_clicked.connect(
            self.ptt_button.key_pressed, Qt.ConnectionType.QueuedConnection
        )
        self.keyboard_signals.key_pressed.connect(
            self.ptt_button.key_pressed, Qt.ConnectionType.QueuedConnection
        )
        self.mouse_signals.mouse_released.connect(
            self.ptt_button.key_released, Qt.ConnectionType.QueuedConnection
        )
        self.keyboard_signals.key_released.connect(
            self.ptt_button.key_released, Qt.ConnectionType.QueuedConnection
        )
        self.joystick_signals.button_pressed.connect(
            self.ptt_button.key_pressed, Qt.ConnectionType.QueuedConnection
        )
        self.joystick_signals.button_released.connect(
            self.ptt_button.key_released, Qt.ConnectionType.QueuedConnection
        )
        self.ptt_button.ptt_pressed.connect(lambda x: self.signals.ptt_status_change.emit(x))
        # 使用同一个状态信号驱动提示音（由 AudioHandler 在用户选择的输出设备上播放）
        self.ptt_button.ptt_pressed.connect(lambda x: self.signals.ptt_beep.emit(x))
        # connection_state_changed 在网络线程中 emit，用 QueuedConnection 保证槽在主线程执行
        self.signals.connection_state_changed.connect(
            self.handle_connect_status_change, Qt.ConnectionType.QueuedConnection
        )

        self.menubar.setVisible(True)
        self.resize_window(600, 600, True)
        self.windows.setCurrentIndex(1)
        self.loading.stop_animation()

    def center(self):
        screen = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.frameGeometry()
        geo.moveCenter(screen)
        self.move(geo.topLeft())

    def handle_connect_status_change(self, status: ConnectionState) -> None:
        match status:
            case ConnectionState.DISCONNECTED:
                self.setWindowTitle(f"{app_title} - 已断开")
            case ConnectionState.CONNECTING:
                self.setWindowTitle(f"{app_title} - 连接中")
            case ConnectionState.CONNECTED:
                self.setWindowTitle(f"{app_title} - 已连接")
            case ConnectionState.AUTHENTICATING:
                self.setWindowTitle(f"{app_title} - 认证中")
            case ConnectionState.READY:
                self.setWindowTitle(f"{app_title} - 已就绪")

    def show_about(self) -> None:
        from src.constants import app_version, organization_name, organization_website
        QMessageBox.about(
            self,
            "关于",
            f"<h3>{app_name}</h3>"
            f"<p>版本 {app_version.version}</p>"
            f"<p>{organization_name}<br/>"
            f"<a href=\"{organization_website}\">{organization_website}</a></p>"
            f"<p>基于 PySide6 的语音客户端，支持管制员与飞行员双角色。</p>"
            f"<p>Copyright © 2025-2026 Half_nothing<br/>MIT License</p>"
        )

    def show_about_qt(self) -> None:
        QMessageBox.aboutQt(self, "关于 Qt")

    def show_config_window(self) -> None:
        if self.config is None:
            return
        self.config.update_config_data()
        self.config.show()

    def resize_window(self, width: int, height: int, to_center: bool) -> None:
        if width > 0 and height > 0:
            self.resize(width, height)
        if to_center:
            self.center()
