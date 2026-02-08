#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
from pathlib import Path
from sys import platform
from threading import Event, Thread
from time import sleep
from typing import Optional
from urllib.parse import urljoin

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHeaderView, QMessageBox, QTableWidget, QTableWidgetItem, QWidget
from loguru import logger

from src.config import config
from src.core import Transmitter, VoiceClient, FSUIPCClient
from src.model import OnlineClientsModel
from src.utils import http
from src.utils import show_error
from .form import Ui_ClientWindow
from src.signal import AudioClientSignals


class ClientWindow(QWidget, Ui_ClientWindow):
    _update_controller_signal = Signal(OnlineClientsModel)
    _fsuipc_client_connected = Signal(bool)
    _com_info_update = Signal(int, int, int, int, bool, bool)

    def __init__(self, signals: AudioClientSignals, voice_client: VoiceClient):
        super().__init__()
        self.setupUi(self)

        self.button_com1_tx.clicked.connect(self.com1_freq_tx_clicked)
        self.button_com2_tx.clicked.connect(self.com2_freq_tx_clicked)
        self.button_com1_rx.clicked.connect(self.com1_rx_clicked)
        self.button_com2_rx.clicked.connect(self.com2_rx_clicked)
        self.label_com1_freq.editingFinished.connect(self.handle_com1_freq)
        self.label_com2_freq.editingFinished.connect(self.handle_com2_freq)
        self.sync_frequency.clicked.connect(self.sync_frequency_changed)
        self.sync_receive_flag.clicked.connect(self.sync_receive_flag_changed)

        self.fsuipc_client: Optional[FSUIPCClient] = None
        self.voice_client = voice_client
        self.signals = signals
        self.thread_exit = Event()
        self.com1_transmitter = Transmitter(122800, 0)
        self.com2_transmitter = Transmitter(121500, 1)
        self.fsuipc_disable = False
        self.fsuipc_connecting = False

        self.label_com1_freq.setText("122.800")
        self.label_com2_freq.setText("121.500")
        self.sync_frequency.setEnabled(False)
        self.sync_receive_flag.setEnabled(False)
        self.button_connect.setEnabled(False)

        self.table_online_controllers.setColumnCount(2)
        self.table_online_controllers.setHorizontalHeaderLabels(["呼号", "频率"])
        self.table_online_controllers.verticalHeader().hide()
        self.table_online_controllers.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_online_controllers.horizontalHeader().hide()
        self.table_online_controllers.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_online_controllers.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_online_controllers.setShowGrid(False)
        self.insert_frequency_row("UNICOM", 122800)
        self.insert_frequency_row("EMER", 121500)

        self._controller_frequency: dict[str, tuple[int, int]] = {}  # 呼号: (频率, 行数)

        self._update_controller_signal.connect(self._update_controller_list)

        self.com1_volume.sliderMoved.connect(self.com1_volume_changed)
        self.com2_volume.sliderMoved.connect(self.com2_volume_changed)
        self._fsuipc_client_connected.connect(self._fsuipc_connected)
        self._com_info_update.connect(self.update_com_info)
        self.button_connect.clicked.connect(self.connect_to_simulator)

    def load_fsuipc_lib(self) -> Optional[FSUIPCClient]:
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
                    return None
            return FSUIPCClient(lib_location)
        except FileNotFoundError:
            logger.error("Cannot find libfsuipc")
            QMessageBox.critical(self, "Cannot load libfsuipc",
                                 f"Cannot found libfsuipc, download it and put it under {lib_path}")
            return None
        except Exception as e:
            logger.error(f"Fail to load libfsuipc, {e}")
            QMessageBox.critical(self, "Cannot load libfsuipc",
                                 "Unknown error occurred while loading libfsuipc")
            return None

    def start(self):
        self.voice_client.add_transmitter(self.com1_transmitter)
        self.voice_client.add_transmitter(self.com2_transmitter)
        self.thread_exit.clear()
        Thread(target=self._update_controller_list_thread, daemon=True).start()
        self.fsuipc_client = self.load_fsuipc_lib()
        if self.fsuipc_client is None:
            self.fsuipc_disable = True
            self.button_connect.setEnabled(False)
            self.signals.show_log_message.emit("FSUIPC", "ERROR", "无法加载 libfsuipc.dll 文件")
        else:
            self.connect_to_simulator()

    def connect_to_simulator(self):
        if self.fsuipc_disable or self.fsuipc_connecting:
            return
        self.fsuipc_connecting = True
        self.button_connect.setText("正在连接模拟器...")
        self.button_connect.setEnabled(False)
        self.label_fsuipc_v.setText("连接中")
        Thread(target=self._connect_to_simulator, daemon=True).start()

    def _fsuipc_connected(self, success: bool):
        self.fsuipc_connecting = False
        self.label_com1_freq.setEnabled(True)
        self.label_com2_freq.setEnabled(True)
        self.button_com1_rx.setEnabled(True)
        self.button_com2_rx.setEnabled(True)
        self.sync_frequency.setChecked(False)
        self.sync_receive_flag.setChecked(False)
        self.sync_frequency.setEnabled(success)
        self.sync_receive_flag.setEnabled(success)

        if success:
            self.button_connect.setText("已连接")
            self.label_fsuipc_v.setText("已连接")
            self.sync_frequency.setChecked(True)
            self.sync_frequency_changed(True)
            Thread(target=self._receive_frequency, daemon=True).start()
            return

        self.button_connect.setText("连接模拟器")
        self.button_connect.setEnabled(True)
        self.label_fsuipc_v.setText("未连接")

    def _connect_to_simulator(self):
        if self.fsuipc_client is None:
            self._fsuipc_client_connected.emit(False)
            return
        retry = 0
        max_retry = 12
        retry_delay = 5
        while True:
            res = self.fsuipc_client.open_fsuipc_client()
            if res.request_status:
                logger.success("FSUIPC connection established")
                self.signals.show_log_message.emit("FSUIPC", "INFO", "FSUIPC连接成功")
                self._fsuipc_client_connected.emit(True)
                break
            logger.error(f"FSUIPC connection failed, {retry + 1}/{max_retry} times")
            retry += 1
            if retry == max_retry:
                logger.error(f"FSUIPC connection failed")
                self.signals.show_log_message.emit("FSUIPC", "ERROR", "FSUIPC连接失败")
                self._fsuipc_client_connected.emit(False)
                break
            sleep(retry_delay)

    def com1_volume_changed(self, value: int):
        self.com1_transmitter.volume = value / 100
        self.label_com1_volume.setText(f"{value / 100:.0%}")

    def com2_volume_changed(self, value: int):
        self.com2_transmitter.volume = value / 100
        self.label_com2_volume.setText(f"{value / 200:.0%}")

    def insert_frequency_row(self, callsign: str, frequency: int):
        row = self.table_online_controllers.rowCount()
        self.table_online_controllers.insertRow(row)

        self.table_online_controllers.setItem(row, 0, QTableWidgetItem(callsign))
        self.table_online_controllers.setItem(row, 1, QTableWidgetItem(f"{frequency / 1000:.3f}"))

    def com1_freq_tx_clicked(self):
        self.button_com2_tx.active = False
        self.com1_transmitter.send_flag = self.button_com1_tx.active
        self.voice_client.update_transmitter(self.com1_transmitter)

    def com2_freq_tx_clicked(self):
        self.button_com1_tx.active = False
        self.com2_transmitter.send_flag = self.button_com2_tx.active
        self.voice_client.update_transmitter(self.com2_transmitter)

    def _update_controller_list(self, data: OnlineClientsModel):
        controllers: set[str] = set()
        for controller in data.controllers:
            if controller.rating <= 1:
                continue
            controllers.add(controller.callsign)
            if controller.callsign not in self._controller_frequency:
                self.insert_frequency_row(controller.callsign, controller.frequency)
                self._controller_frequency[controller.callsign] = (controller.frequency,
                                                                   self.table_online_controllers.rowCount() - 1)
            else:
                frequency, row = self._controller_frequency[controller.callsign]
                if frequency != controller.frequency:
                    self.table_online_controllers.setItem(row, 1,
                                                          QTableWidgetItem(f"{controller.frequency / 1000:.3f}"))
        for callsign, (frequency, row) in list(self._controller_frequency.items()):
            if callsign not in controllers:
                self.table_online_controllers.removeRow(row)
                del self._controller_frequency[callsign]
        for i in range(2, self.table_online_controllers.rowCount()):
            c = self.table_online_controllers.item(i, 0)
            if c is None:
                continue
            key = c.text()
            if key not in self._controller_frequency:
                continue
            self._controller_frequency[key] = (self._controller_frequency[key][0], i)

    def sync_frequency_changed(self, checked: bool):
        self.label_com1_freq.setEnabled(not checked)
        self.label_com2_freq.setEnabled(not checked)

    def sync_receive_flag_changed(self, checked: bool):
        self.button_com1_rx.setEnabled(not checked)
        self.button_com2_rx.setEnabled(not checked)

    def handle_com1_freq(self):
        if self.sync_frequency.isChecked():
            return
        frequency = int(float(self.label_com1_freq.text()) * 1000)
        if frequency < 3000 or frequency > 200000:
            show_error(self.label_com1_freq)
            return
        if self.com1_transmitter.frequency == frequency:
            return
        self.com1_transmitter.frequency = frequency
        self.voice_client.update_transmitter(self.com1_transmitter)

    def handle_com2_freq(self):
        if self.sync_frequency.isChecked():
            return
        frequency = int(float(self.label_com2_freq.text()) * 1000)
        if frequency < 3000 or frequency > 200000:
            show_error(self.label_com2_freq)
            return
        if self.com2_transmitter.frequency == frequency:
            return
        self.com2_transmitter.frequency = frequency
        self.voice_client.update_transmitter(self.com2_transmitter)

    def com1_rx_clicked(self):
        if self.sync_receive_flag.isChecked():
            return
        self.com1_transmitter.receive_flag = self.button_com1_rx.active
        self.voice_client.update_transmitter(self.com1_transmitter)

    def com2_rx_clicked(self):
        if self.sync_receive_flag.isChecked():
            return
        self.com2_transmitter.receive_flag = self.button_com2_rx.active
        self.voice_client.update_transmitter(self.com2_transmitter)

    def stop(self):
        self.thread_exit.set()

    def _update_controller_list_thread(self):
        while not self.thread_exit.is_set():
            response = http.client.get(urljoin(config.server.api_endpoint, "/api/clients"))
            if response.status_code != 200:
                logger.error(f"Error while getting clients from server: {response.status_code}")
                return
            data = OnlineClientsModel.model_validate_json(response.content)
            self._update_controller_signal.emit(data)
            sleep(15)

    def _receive_frequency(self):
        if self.fsuipc_disable or self.fsuipc_connecting or self.fsuipc_client is None:
            return
        err_count = 0
        while not self.thread_exit.is_set():
            res = self.fsuipc_client.get_frequency()
            if res.request_status:
                self._com_info_update.emit(res.frequency[0] // 1000,
                                           res.frequency[1] // 1000,
                                           res.frequency[2] // 1000,
                                           res.frequency[3] // 1000,
                                           (res.frequency_flag & 0x80) != 0x80,
                                           (res.frequency_flag & 0x40) != 0x40)
                err_count = 0
            else:
                logger.error(f"Error while receiving frequency from FSUIPC: {res.err_message}")
                err_count += 1
            if err_count >= 3:
                logger.error(f"Too many error received from FSUIPC: {err_count}, disconnecting")
                self.signals.show_log_message.emit("FSUIPC", "ERROR", "读取频率错误")
                self._fsuipc_client_connected.emit(False)
                break
            sleep(1)

    def _update_frequency(self, com1_freq: int, com2_freq: int):
        if self.com1_transmitter.frequency != com1_freq:
            self.label_com1_freq.setText(f"{com1_freq / 1000:.3f}")
            self.com1_transmitter.frequency = com1_freq
            self.voice_client.update_transmitter(self.com1_transmitter)

        if self.com2_transmitter.frequency != com2_freq:
            self.label_com2_freq.setText(f"{com2_freq / 1000:.3f}")
            self.com2_transmitter.frequency = com2_freq
            self.voice_client.update_transmitter(self.com2_transmitter)

    def _update_receive(self, com1_rx: bool, com2_rx: bool):
        if self.com1_transmitter.receive_flag != com1_rx:
            self.com1_transmitter.receive_flag = com1_rx
            self.button_com1_rx.active = com1_rx
            self.voice_client.update_transmitter(self.com1_transmitter)

        if self.com2_transmitter.receive_flag != com2_rx:
            self.com2_transmitter.receive_flag = com2_rx
            self.button_com2_rx.active = com2_rx
            self.voice_client.update_transmitter(self.com2_transmitter)

    def update_com_info(self, com1_freq: int, com1_standby: int, com2_freq: int, com2_standby: int,
                        com1_rx: bool, com2_rx: bool):
        self.com1_active_v.setText(f"{com1_freq / 1000:.3f}")
        self.com1_standby_v.setText(f"{com1_standby / 1000:.3f}")
        self.com1_receive_v.setText(f"{'是' if com1_rx else '否'}")
        self.com2_active_v.setText(f"{com2_freq / 1000:.3f}")
        self.com2_standby_v.setText(f"{com2_standby / 1000:.3f}")
        self.com2_receive_v.setText(f"{'是' if com2_rx else '否'}")

        if self.sync_frequency.isChecked():
            self._update_frequency(com1_freq, com2_freq)

        if self.sync_receive_flag.isChecked():
            self._update_receive(com1_rx, com2_rx)
