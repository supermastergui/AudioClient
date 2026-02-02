#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, socket
from struct import unpack
from threading import Thread
from time import time
from typing import Optional

from PySide6.QtCore import QObject, QTimer
from loguru import logger
from pydantic import ValidationError

from src.model import ClientInfo, ControlMessage, MessageType, VoicePacket, VoicePacketBuilder
from src.signal import AudioClientSignals


# 网络处理器
class NetworkHandler(QObject):
    def __init__(self, signals: AudioClientSignals, client_info: ClientInfo):
        super().__init__()

        # 双协议, TCP用于传输信令, UDP用于传输音频数据
        self._tcp_socket: Optional[socket] = None
        self._udp_socket: Optional[socket] = None
        self._server_address: Optional[tuple] = None

        self._signals = signals
        self._client_info = client_info

        self._tcp_running = False
        self._udp_running = False
        self._connected = False

        self._heartbeat_timer = QTimer()
        self._heartbeat_timer.timeout.connect(self._heartbeat_send_handler)
        self._heartbeat_timer.setInterval(15000)

        self._empty_voice_packet = VoicePacketBuilder.build_packet(client_info.cid, 0, 0,
                                                                   client_info.callsign, b"")

    def _log_message(self, level: str, message: str):
        self._signals.log_message.emit("Network", level, message)

    def _show_log_message(self, level: str, message: str):
        self._signals.show_log_message.emit("Network", level, message)

    def _heartbeat_send_handler(self):
        if not self._connected:
            return
        message = ControlMessage(type=MessageType.PING, cid=self._client_info.cid,
                                 callsign=self._client_info.callsign, data=str(int(time())))
        self.send_control_message(message)
        self.send_voice_packet(self._empty_voice_packet)

    # 连接到服务器
    def connect_to_server(self, host: str, tcp_port: int, udp_port: int, jwt_token: str):
        try:
            self._server_address = (host, udp_port)

            # 首先连接TCP信道
            self._log_message("INFO", f"Connect to tcp://{host}:{tcp_port}")
            self._tcp_socket = socket(AF_INET, SOCK_STREAM)
            self._tcp_socket.connect((host, tcp_port))
            self._tcp_running = True
            tcp_thread = Thread(target=self._tcp_receive_loop, daemon=True)
            tcp_thread.start()

            # 然后连接UDP信道
            self._log_message("INFO", f"Connect to udp://{host}:{udp_port}")
            self._udp_socket = socket(AF_INET, SOCK_DGRAM)
            self._udp_socket.connect((host, udp_port))
            self._udp_running = True
            udp_thread = Thread(target=self._udp_receive_loop, daemon=True)
            udp_thread.start()

            # 发送令牌验证
            self._tcp_socket.send(f"{jwt_token}\n".encode())
            self._connected = True
            self._signals.socket_connection_state.emit(True)
            self._log_message("INFO", "Connected to voice server")
            self._show_log_message("INFO", "连接服务器成功")
            self._empty_voice_packet = VoicePacketBuilder.build_packet(self._client_info.cid, 0, 0,
                                                                       self._client_info.callsign, b"")
            self._heartbeat_timer.start()
        except Exception as e:
            self._log_message("ERROR", f"Failed to connect to server")
            self._signals.error_occurred.emit(f"连接失败: {e}")
            self.cleanup()

    # 断开连接
    def disconnect_from_server(self):
        # 发送断开连接消息
        self.send_control_message(ControlMessage(type=MessageType.DISCONNECT, cid=self._client_info.cid))
        self.cleanup()
        self._signals.socket_connection_state.emit(False)
        self._log_message("INFO", f"Disconnected from voice server")

    # 发送信令消息
    def send_control_message(self, message: ControlMessage):
        if not self._tcp_socket:
            return
        try:
            self._tcp_socket.send(message.model_dump_json().encode(encoding="utf-8") + b'\n')
        except UnicodeEncodeError as e:
            self._log_message("ERROR", f"Failed to send control message, encoding error: {e}")
        except WindowsError as e:
            self._log_message("ERROR", f"Failed to send control message, windows error: {e}")
        except Exception as e:
            self._log_message("ERROR", f"Failed to send control message, unknown error: {e}")

    # 发送音频数据
    def send_voice_packet(self, packet: bytes):
        if not self._udp_socket or not self._server_address:
            return

        try:
            self._udp_socket.sendto(packet, self._server_address)
        except Exception as e:
            self._log_message("ERROR", f"Failed to send voice packet: {e}")

    # 接收信令
    def _tcp_receive_loop(self):
        data_buffer = b""
        while self._tcp_running and self._tcp_socket:
            try:
                data = self._tcp_socket.recv(4096)
                if not data:
                    break
                self._log_message("TRACE",
                                  f"TCP > receive from server: {data.decode('utf-8', 'ignore').replace('\n', '')}")
                data_buffer += data
                if b'\n' in data_buffer:
                    data, data_buffer = data_buffer.split(b'\n', 1)
                    self._process_control_message(data)
                elif len(data_buffer) > 4096:
                    self._log_message("ERROR", "TCP > receive buffer overflow")
                    data_buffer = b""
            except Exception as e:
                if self._tcp_running:
                    self._log_message("ERROR", f"TCP > receive error: {e}")
                break
        self.disconnect_from_server()

    # 接收音频数据
    def _udp_receive_loop(self):
        while self._udp_running and self._udp_socket:
            try:
                data, addr = self._udp_socket.recvfrom(65507)
                self._process_voice_packet(data)
            except Exception as e:
                if self._udp_running:
                    self._log_message("ERROR", f"UDP receive error: {e}")
                break

    # 处理信令
    def _process_control_message(self, data: bytes):
        try:
            self._signals.control_message_received.emit(ControlMessage.model_validate_json(data))
        except ValidationError as e:
            logger.error(f"Failed to parse control message: {e}")
        except Exception as e:
            logger.error(f"Failed to process control message: {e}")

    # 处理音频数据
    def _process_voice_packet(self, data: bytes):
        try:
            if len(data) < 10 or data[-1] != 0x0A:
                return
            cid = unpack('<i', data[0:4])[0]
            transmitter = unpack('<b', data[4:5])[0]
            frequency = unpack('<i', data[5:9])[0]
            callsign_len = data[9]
            if 9 + callsign_len > len(data) - 1:
                return
            callsign = data[10:10 + callsign_len].decode("utf-8")
            audio_data = data[10 + callsign_len:-1]
            logger.trace(
                f"Received from {callsign} (CID={cid}, Frequency={frequency}), audio length: {len(audio_data)}")
            packet = VoicePacket(cid, transmitter, frequency, callsign, audio_data)
            self._signals.voice_data_received.emit(packet)
        except Exception as e:
            logger.error(f"Failed to process voice packet: {e}")

    def cleanup(self):
        self._tcp_running = False
        self._udp_running = False
        self._connected = False

        self._heartbeat_timer.stop()

        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except:
                pass
            self._tcp_socket = None

        if self._udp_socket:
            try:
                self._udp_socket.close()
            except:
                pass
            self._udp_socket = None

    def shutdown(self):
        self.cleanup()
