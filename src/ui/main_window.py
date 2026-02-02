#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from asyncio import get_running_loop, new_event_loop, set_event_loop
from threading import Thread
from typing import Optional

from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QMainWindow
from loguru import logger

from src.config import config, config_manager
from src.constants import app_title
from src.core import VoiceClient, WebSocketBroadcastServer
from src.model import ConnectionState
from src.signal import AudioClientSignals, KeyBoardSignals, MouseSignals
from src.thread import KeyboardListenerThread, MouseListenerThread
from src.utils import http
from .component import PTTButton
from .config_window import ConfigWindow
from .connect_window import ConnectWindow
from .form import Ui_MainWindow
from .loading_window import LoadingWindow
from .login_window import LoginWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, signals: AudioClientSignals, mouse_signals: MouseSignals,
                 keyboard_signals: KeyBoardSignals) -> None:
        super().__init__()
        logger.trace("Creating main window")

        self.setupUi(self)
        self.resize(300, 300)
        self.setMinimumSize(300, 300)
        self.setWindowTitle(app_title)
        self.menubar.setVisible(False)

        self.voice_client: Optional[VoiceClient] = None
        self.keyboard_listener: Optional[KeyboardListenerThread] = None
        self.mouse_listener: Optional[MouseListenerThread] = None
        self.connect_window: Optional[ConnectWindow] = None
        self.login: Optional[LoginWindow] = None
        self.config: Optional[ConfigWindow] = None
        self.ptt_button: Optional[PTTButton] = None

        self.loading = LoadingWindow()
        self.loading.setObjectName(u"loading")
        self.windows.addWidget(self.loading)
        self.windows.setCurrentIndex(0)

        self.websocket = WebSocketBroadcastServer()
        signals.broadcast_message.connect(lambda msg: self.websocket.broadcast(msg))
        Thread(target=self.start_websocket, daemon=True).start()

        self.signals = signals
        self.mouse_signals = mouse_signals
        self.keyboard_signals = keyboard_signals

        config_manager.register_save_callback(self.config_update)

        http.initialize()
        http.client_initialized.connect(self.initialize_complete)
        self.action_settings.triggered.connect(self.show_config_window)
        signals.show_config_windows.connect(self.show_config_window)
        signals.logout_request.connect(self.logout_request)
        signals.resize_window.connect(self.resize_window)

    def start_websocket(self):
        try:
            loop = get_running_loop()
        except RuntimeError:
            loop = new_event_loop()
            set_event_loop(loop)
        loop.run_until_complete(self.websocket.start())

    def logout_request(self) -> None:
        if self.voice_client is not None:
            self.voice_client.client_info.reset()
        self.windows.setCurrentIndex(1)
        self.resize_window(600, 600, True)

    def login_success(self) -> None:
        self.resize_window(600, 300, True)
        self.windows.setCurrentIndex(2)

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

        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.config.button_ptt.mouse_signal = self.mouse_signals
        self.config.button_ptt.keyboard_signal = self.keyboard_signals

        self.ptt_button = PTTButton()
        self.config_update()
        self.mouse_signals.mouse_clicked.connect(self.ptt_button.key_pressed)
        self.keyboard_signals.key_pressed.connect(self.ptt_button.key_pressed)
        self.mouse_signals.mouse_released.connect(self.ptt_button.key_released)
        self.keyboard_signals.key_released.connect(self.ptt_button.key_released)
        self.ptt_button.ptt_pressed.connect(lambda x: self.signals.ptt_status_change.emit(x))
        self.signals.connection_state_changed.connect(self.handle_connect_status_change)

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
