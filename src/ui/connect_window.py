#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from datetime import datetime
from os import getcwd
from os.path import join
from sys import platform
from threading import Thread
from time import sleep, time

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QMessageBox, QWidget
from loguru import logger

from .client_window import ClientWindow
from .controller_window import ControllerWindow
from .form import Ui_ConnectWindow
from src.config import config
from src.core import VoiceClient, FSUIPCClient
from src.model import ConnectionState, RxBegin, RxEnd, VoiceConnectedState, VoicePacket, WebSocketMessage
from src.signal import AudioClientSignals
from src.constants import default_frame_time, default_frame_time_s


class ConnectWindow(QWidget, Ui_ConnectWindow):
    fsuipc_client_connected = Signal()
    fsuipc_client_connect_fail = Signal()

    def __init__(self, voice_client: VoiceClient, signals: AudioClientSignals):
        super().__init__()
        self.setupUi(self)

        try:
            if platform == 'win32':
                lib_location = join(getcwd(), "lib/libfsuipc.dll")
            elif platform == 'darwin':
                lib_location = join(getcwd(), "lib/libfsuipc.dylib")
            elif platform == 'linux':
                lib_location = join(getcwd(), "lib/libfsuipc.so")
            else:
                raise OSError("unknown platform")

            self.fsuipc_client = FSUIPCClient(lib_location)
        except FileNotFoundError:
            logger.error("Cannot find libfsuipc")
            QMessageBox.critical(self, "Cannot load libfsuipc",
                                 f"Cannot found libfsuipc, download it and put it under {join(getcwd(), 'lib')}")
            exit(1)
        except Exception as e:
            logger.error(f"Fail to load libfsuipc, {e}")
            QMessageBox.critical(self, "Cannot load libfsuipc",
                                 "Unknown error occurred while loading libfsuipc")
            exit(1)

        self.voice_client = voice_client
        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_exit.clicked.connect(lambda: signals.logout_request.emit())
        self.voice_client.signals.error_occurred.connect(self.handle_connect_error)
        self.voice_client.signals.connection_state_changed.connect(self.connect_state_changed)
        self.controller_window = ControllerWindow(voice_client)
        self.client_window = ClientWindow(voice_client, self.fsuipc_client)
        self.windows.addWidget(QWidget())
        self.windows.addWidget(self.controller_window)
        self.windows.addWidget(self.client_window)
        self.windows.setCurrentIndex(0)
        self.fsuipc_client_connected.connect(self.fsuipc_connect)
        self.fsuipc_client_connect_fail.connect(self.fsuipc_connection_fail)
        signals.show_log_message.connect(self.log_message)

        self.voice_client.signals.voice_data_sent.connect(self.tx_send)
        self.voice_client.signals.voice_data_received.connect(self.rx_receive)
        self.last_data_receive: float = 0.0
        self.receive_timeout_timer = QTimer()
        self.receive_timeout_timer.timeout.connect(self.check_rx_timeout)
        self.receive_timeout_timer.setInterval(default_frame_time // 4)
        self.receive_timeout_timer.start()
        self.last_data_send: float = 0.0
        self.send_timeout_timer = QTimer()
        self.send_timeout_timer.timeout.connect(self.check_tx_timeout)
        self.send_timeout_timer.setInterval(default_frame_time // 4)
        self.send_timeout_timer.start()

        self._connected = False
        self.signals = signals

    def check_rx_timeout(self):
        if self.button_rx.is_active:
            diff = time() - self.last_data_receive
            if diff > default_frame_time_s * 4:
                self.button_rx.set_active(False)
                self.signals.broadcast_message.emit(WebSocketMessage(RxEnd(
                    [item for item in self.voice_client.receiving.keys()],
                    self.label_rx_callsign_v.text(),
                    int(float(self.label_rx_freq_v.text()) * 1000000)
                )))

    def check_tx_timeout(self):
        if self.button_tx.is_active:
            if time() - self.last_data_send > default_frame_time_s:
                self.button_tx.set_active(False)

    def tx_send(self) -> None:
        if self.voice_client.connection_state != ConnectionState.READY:
            self.button_tx.set_active(False)
            return
        self.last_data_send = time()
        self.button_tx.set_active(True)

    def rx_receive(self, voice: VoicePacket) -> None:
        if self.voice_client.connection_state != ConnectionState.READY:
            self.button_rx.set_active(False)
            return
        if not self.button_rx.is_active:
            self.signals.broadcast_message.emit(
                WebSocketMessage(RxBegin([item for item in self.voice_client.receiving.keys()], voice.callsign,
                                         voice.frequency * 1000)))
        self.last_data_receive = time()
        self.button_rx.set_active(True)
        self.label_rx_callsign_v.setText(voice.callsign)
        self.label_rx_freq_v.setText(f"{voice.frequency / 1000:.3f}")

    def login_success(self):
        if self.voice_client.client_info.cid is None:
            return
        self.label_cid_v.setText(f"{self.voice_client.client_info.cid:04}")

    def connect_to_server(self):
        if self._connected:
            self.voice_client.disconnect_from_server()
            self.client_window.stop()
            self._connected = False
            return

        self.voice_client.connect_to_server(
            config.server.voice_endpoint,
            config.server.voice_tcp_port,
            config.server.voice_udp_port
        )

    def connect_state_changed(self, state: ConnectionState):
        if state == ConnectionState.READY:
            self.button_connect.setText("断开连接")
            self._connected = True
            self.signals.broadcast_message.emit(WebSocketMessage(VoiceConnectedState(True)))
            self.label_callsign_v.setText(self.voice_client.client_info.callsign)
            self.log_message("Network", "INFO", "成功连接至服务器")
            if self.voice_client.client_info.is_atc:
                self.windows.setCurrentIndex(1)
            else:
                Thread(target=self.connect_to_simulator, daemon=True).start()
        elif state == ConnectionState.DISCONNECTED:
            self._connected = False
            self.signals.broadcast_message.emit(WebSocketMessage(VoiceConnectedState(False)))
            self.button_connect.setText("连接服务器")
            self.log_message("Network", "INFO", "断开连接")
            self.label_callsign_v.setText("----")
            self.windows.setCurrentIndex(0)

    def fsuipc_connect(self):
        self.windows.setCurrentIndex(2)
        self.signals.resize_window.emit(450, 600, True)
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
            if res.requestStatus:
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
