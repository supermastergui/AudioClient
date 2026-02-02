#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from datetime import datetime
from pathlib import Path
from sys import platform
from threading import Thread
from time import sleep, time

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QMessageBox, QWidget
from loguru import logger

from src.config import config
from src.constants import default_frame_time, default_frame_time_s
from src.core import FSUIPCClient, VoiceClient
from src.model import ConnectionState, VoicePacket, WebSocketMessage
from src.signal import AudioClientSignals
from .client_window import ClientWindow
from .controller_window import ControllerWindow
from .form import Ui_ConnectWindow


class ConnectWindow(QWidget, Ui_ConnectWindow):
    fsuipc_client_connected = Signal()
    fsuipc_client_connect_fail = Signal()

    def __init__(self, signals: AudioClientSignals, voice_client: VoiceClient):
        super().__init__()
        self.setupUi(self)

        self.voice_client = voice_client
        self.signals = signals
        self.connected = False
        self.fsuipc_client = self.load_fsuipc_lib()
        self.active_transmitter: dict[str, tuple[float, int]] = {}
        self.controller_window = ControllerWindow(signals, voice_client)
        self.client_window = ClientWindow(voice_client, self.fsuipc_client)
        self.windows.addWidget(QWidget())
        self.windows.setCurrentIndex(0)

        self.receive_timeout_timer = QTimer()
        self.receive_timeout_timer.timeout.connect(self.check_rx_timeout)
        self.receive_timeout_timer.setInterval(default_frame_time // 4)
        self.receive_timeout_timer.start()

        self.last_data_send: float = 0.0
        self.send_timeout_timer = QTimer()
        self.send_timeout_timer.timeout.connect(self.check_tx_timeout)
        self.send_timeout_timer.setInterval(default_frame_time // 4)
        self.send_timeout_timer.start()

        self.signals.error_occurred.connect(self.handle_connect_error)
        self.signals.connection_state_changed.connect(self.connect_state_changed)
        self.signals.show_log_message.connect(self.log_message)

        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_exit.clicked.connect(lambda: signals.logout_request.emit())
        self.fsuipc_client_connected.connect(self.fsuipc_connect)
        self.fsuipc_client_connect_fail.connect(self.fsuipc_connection_fail)
        self.voice_client.signals.voice_data_sent.connect(self.tx_send)
        self.voice_client.signals.voice_data_received.connect(self.rx_receive)
        self.signals.login_success.connect(self.login_success)

    def load_fsuipc_lib(self) -> FSUIPCClient:
        lib_path = Path.cwd() / "lib"
        try:
            match platform:
                case 'win32':
                    lib_location = lib_path / "libfsuipc.dll"
                case 'darwin':
                    lib_location = lib_path / "libfsuipc.dylib"
                case 'linux':
                    lib_location = lib_path / "libfsuipc.so"
                case _:
                    raise OSError("unknown platform")
            return FSUIPCClient(lib_location)
        except FileNotFoundError:
            logger.error("Cannot find libfsuipc")
            QMessageBox.critical(self, "Cannot load libfsuipc",
                                 f"Cannot found libfsuipc, download it and put it under {lib_path}")
            exit(1)
        except Exception as e:
            logger.error(f"Fail to load libfsuipc, {e}")
            QMessageBox.critical(self, "Cannot load libfsuipc",
                                 "Unknown error occurred while loading libfsuipc")
            exit(1)

    def check_rx_timeout(self):
        current_time = time()
        for transmitter, data in list(self.active_transmitter.items()):
            if current_time - data[0] > default_frame_time_s * 4:
                self.signals.broadcast_message.emit(WebSocketMessage.rx_end(transmitter, data[1]))
                del self.active_transmitter[transmitter]
        active = len(self.active_transmitter) > 0
        self.button_rx.set_active(active)
        if self.voice_client.client_info.is_atc:
            self.controller_window.sub_window.button_rx.set_active(active)

    def check_tx_timeout(self):
        if not self.button_tx.is_active:
            return
        if time() - self.last_data_send < default_frame_time_s:
            return
        self.button_tx.set_active(False)
        if self.voice_client.client_info.is_atc:
            self.controller_window.sub_window.button_tx.set_active(False)

    def tx_send(self) -> None:
        if self.voice_client.connection_state != ConnectionState.READY:
            self.button_tx.set_active(False)
            self.controller_window.sub_window.button_tx.set_active(False)
            return
        self.last_data_send = time()
        self.button_tx.set_active(True)
        if self.voice_client.client_info.is_atc:
            self.controller_window.sub_window.button_tx.set_active(True)

    def rx_receive(self, voice: VoicePacket) -> None:
        if self.voice_client.connection_state != ConnectionState.READY:
            self.button_rx.set_active(False)
            self.controller_window.sub_window.button_rx.set_active(False)
            return
        if self.active_transmitter.get(voice.callsign, None) is None:
            self.signals.broadcast_message.emit(
                WebSocketMessage.rx_begin(voice.callsign, voice.frequency * 1000)
            )
        self.active_transmitter[voice.callsign] = (time(), voice.frequency * 1000)
        self.button_rx.set_active(True)
        self.label_rx_callsign_v.setText(voice.callsign)
        self.label_rx_freq_v.setText(f"{voice.frequency / 1000:.3f}")
        if self.voice_client.client_info.is_atc:
            self.controller_window.sub_window.button_rx.set_active(True)
            self.controller_window.sub_window.label_rx_callsign_v.setText(voice.callsign)

    def login_success(self):
        if self.voice_client.client_info.cid is None:
            return
        self.label_cid_v.setText(f"{self.voice_client.client_info.cid:04}")

    def connect_to_server(self) -> None:
        if self.connected:
            self.voice_client.disconnect_from_server()
            self.client_window.stop()
            self.connected = False
            self.button_connect.active = False
            return

        self.voice_client.connect_to_server(
            config.server.voice_endpoint,
            config.server.voice_tcp_port,
            config.server.voice_udp_port
        )

    def connect_state_changed(self, state: ConnectionState):
        if state == ConnectionState.READY:
            self.button_connect.setText("断开连接")
            self.connected = True
            self.button_connect.active = True
            self.button_exit.setEnabled(False)
            self.signals.broadcast_message.emit(WebSocketMessage.voice_connected_state(True))
            self.label_callsign_v.setText(self.voice_client.client_info.callsign)
            self.log_message("Network", "INFO", f"身份认证通过, 欢迎您, {self.voice_client.client_info.cid:04}")
            if self.voice_client.client_info.is_atc:
                self.windows.removeWidget(self.windows.widget(0))
                self.windows.addWidget(self.controller_window)
                self.windows.setCurrentIndex(0)
                self.signals.resize_window.emit(0, 0, True)
            else:
                Thread(target=self.connect_to_simulator, daemon=True).start()
        elif state == ConnectionState.DISCONNECTED:
            self.connected = False
            self.button_connect.active = False
            self.button_exit.setEnabled(True)
            self.signals.broadcast_message.emit(WebSocketMessage.voice_connected_state(False))
            self.button_connect.setText("连接服务器")
            self.log_message("Network", "INFO", "断开连接")
            self.label_callsign_v.setText("----")
            self.windows.removeWidget(self.windows.widget(0))
            self.windows.addWidget(QWidget())
            self.windows.setCurrentIndex(0)
            self.signals.resize_window.emit(600, 300, True)

    def fsuipc_connect(self):
        self.windows.removeWidget(self.windows.widget(0))
        self.windows.addWidget(self.client_window)
        self.windows.setCurrentIndex(0)
        self.client_window.start()

    def fsuipc_connection_fail(self):
        self.connect_to_server()
        QMessageBox.critical(self, "无法连接到模拟器", "无法连接到模拟器, 请检查FSUIPC/XPUIPC是否正确安装")

    def connect_to_simulator(self):
        retry = 0
        max_retry = 12
        retry_delay = 5
        while retry < max_retry:
            res = self.fsuipc_client.open_fsuipc_client()
            if res.request_status:
                logger.success("FSUIPC connection established")
                self.log_message("FSUIPC", "INFO", "FSUIPC连接成功")
                break
            logger.error(f"FSUIPC connection failed, {retry + 1}/{max_retry} times")
            self.log_message("FSUIPC", "ERROR", f"FSUIPC连接失败, 第 {retry + 1}/{max_retry} 次尝试")
            retry += 1
            sleep(retry_delay)
        if retry == max_retry:
            logger.error(f"FSUIPC connection failed")
            self.log_message("FSUIPC", "ERROR", "FSUIPC连接失败")
            self.fsuipc_client_connect_fail.emit()
            return
        self.signals.resize_window.emit(740, 710, True)
        self.fsuipc_client_connected.emit()

    def handle_connect_error(self, message: str) -> None:
        QMessageBox.critical(self, "连接服务器失败", message)
        self.button_connect.setText("连接服务器")
        self.label_callsign_v.setText("----")
        self.windows.setCurrentIndex(0)

    def log_message(self, name: str, level: str, message: str) -> None:
        self.text_browser_log.append(
            f"{datetime.now().strftime('%H:%M:%S')} | {name} | {level.upper()} | {message}")
        cursor = self.text_browser_log.textCursor()
        self.text_browser_log.moveCursor(cursor.MoveOperation.End)
