#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
"""
语音客户端：维护本机 transmitter 列表与频率索引，处理信令与语音包，
将收到的语音按 packet.frequency 路由到对应 transmitter 播放。
"""
from time import time

from PySide6.QtCore import QObject
from loguru import logger

from src.constants import default_frame_time_s
from src.model import ClientInfo, ConnectionState, ControlMessage, MessageType, UserLoginModel, VoicePacket, \
    VoicePacketBuilder
from src.signal import AudioClientSignals
from .audio_handler import AudioHandler
from .network_handler import NetworkHandler
from .transmitter import Transmitter


class VoiceClient(QObject):
    """语音业务入口：网络 + 音频，管理 transmitter、频率索引、当前发送通道与冲突判定。"""

    def __init__(self, signals: AudioClientSignals):
        super().__init__()

        self.signals = signals
        self.client_info = ClientInfo()

        self._connection_state = ConnectionState.DISCONNECTED
        self._network = NetworkHandler(signals, self.client_info)
        self._audio = AudioHandler(signals)
        self._transmitters: dict[int, Transmitter] = {}  # id -> transmitter
        self._transmitters_by_frequency: dict[int, Transmitter] = {}  # frequency -> transmitter（后端限制同用户同频仅一台）
        self._last_receive: dict[int, tuple[str, float]] = {}  # frequency -> (callsign, time)
        self._current_transmitter_id = -1
        self._sending = False

        self._audio.on_encoded_audio = self._send_voice_data
        self.signals.control_message_received.connect(self._handle_control_message)
        self.signals.voice_data_received.connect(self._handle_voice_packet)
        self.signals.socket_connection_state.connect(self._handle_connection_status)
        self.signals.ptt_status_change.connect(self.ptt_state)

    def ptt_state(self, state: bool):
        self._sending = state

    @property
    def client_ready(self) -> bool:
        return self._connection_state == ConnectionState.READY and self.client_info.client_valid

    @property
    def audio(self) -> AudioHandler:
        return self._audio

    @property
    def connection_state(self) -> ConnectionState:
        return self._connection_state

    def connect_to_server(self, host: str, tcp_port: int, udp_port: int):
        self._set_connection_state(ConnectionState.CONNECTING)
        self._network.connect_to_server(host, tcp_port, udp_port, self.client_info.jwt_token)

    def disconnect_from_server(self):
        self._network.disconnect_from_server()
        self._current_transmitter_id = -1
        self._audio.cleanup()
        self._transmitters.clear()
        self._transmitters_by_frequency.clear()
        self.client_info.clear()

    def update_client_info(self, data: UserLoginModel):
        self.client_info.cid = data.user.cid
        self.client_info.jwt_token = data.token
        self.client_info.flush_token = data.flush_token
        self.client_info.user = data.user

    def _rebuild_frequency_index(self) -> None:
        """按频率重建索引（后端限制同用户同频仅一台 transmitter）。"""
        self._transmitters_by_frequency = {
            tx.frequency: tx for tx in self._transmitters.values() if tx.frequency != 0
        }

    def add_transmitter(self, transmitter: Transmitter):
        self._transmitters[transmitter.id] = transmitter
        self._audio.add_transmitter(transmitter)
        self._rebuild_frequency_index()
        if transmitter.frequency == 0:
            return
        self.update_transmitter(transmitter)

    def set_transmitter_output_target(self, transmitter: Transmitter) -> None:
        self._audio.set_transmitter_output_target(transmitter)

    def update_transmitter(self, transmitter: Transmitter):
        if not self.client_ready:
            return

        if not isinstance(transmitter, Transmitter):
            raise ValueError("Invalid transmitter")

        self._rebuild_frequency_index()
        frequency = transmitter.frequency
        rx = transmitter.receive_flag
        transmitter_id = transmitter.id

        if transmitter.send_flag:
            self.signals.update_current_frequency.emit(frequency)
            self._current_transmitter_id = transmitter_id

        message = ControlMessage(
            type=MessageType.SWITCH,
            cid=self.client_info.cid,
            callsign=self.client_info.callsign,
            transmitter=transmitter_id,
            data=f"{frequency}:{'1' if rx else '0'}"
        )
        logger.debug(f"VoiceClient > transmitter info update {transmitter}")
        self._network.send_control_message(message)

    def send_text_message(self, target: str, message: str):
        if not self.client_ready:
            return

        control_message = ControlMessage(
            type=MessageType.MESSAGE,
            cid=self.client_info.cid,
            callsign=self.client_info.callsign,
            data=f"{target}:{message}"
        )
        self._network.send_control_message(control_message)

    def _set_connection_state(self, state: ConnectionState):
        if self._connection_state != state:
            self._connection_state = state
            self.signals.connection_state_changed.emit(state)

    def _send_voice_data(self, encoded_data: bytes):
        if not self.client_ready or self._current_transmitter_id == -1:
            return

        transmitter = self._transmitters.get(self._current_transmitter_id, None)
        if transmitter is None:
            return

        self.signals.voice_data_sent.emit()
        packet = VoicePacketBuilder.build_packet(self.client_info.cid,
                                                 transmitter.id,
                                                 transmitter.frequency,
                                                 self.client_info.callsign,
                                                 encoded_data)
        self._network.send_voice_packet(packet)

    def _handle_control_message(self, message: ControlMessage):
        if message.type == MessageType.ERROR:
            logger.error(f"VoiceClient > server error: {message.data}")
            self.signals.error_occurred.emit(message.data)
        elif message.type == MessageType.PONG:
            logger.debug("VoiceClient > received pong from server")
        elif message.type == MessageType.MESSAGE:
            if message.data.startswith("SERVER:"):
                if "Welcome" in message.data:
                    data = message.data.split(":")
                    self.client_info.callsign = data[1]
                    self._audio.start()
                    if len(data) == 4:
                        self.client_info.main_frequency = int(data[-1])
                        self.client_info.is_atc = True
                    self._set_connection_state(ConnectionState.READY)
                    logger.success("VoiceClient > identity verification passed")
        elif message.type == MessageType.DISCONNECT:
            self.clear()
            self._set_connection_state(ConnectionState.DISCONNECTED)

    def _handle_voice_packet(self, packet: VoicePacket):
        conflict = False
        last_receive = self._last_receive.get(packet.frequency, None)
        if self._sending or (last_receive is not None
                             and time() - last_receive[1] < default_frame_time_s * 5
                             and last_receive[0] != packet.callsign):
            # 如果同时在发送, 或者5个音频帧内收到了多个发送者发来的数据, 则判定为冲突
            conflict = True
        else:
            self._last_receive[packet.frequency] = (packet.callsign, time())
        # 服务端转发的是发送方原始数据，packet.transmitter 是发送方 id；用频率索引 O(1) 查找本机 transmitter
        transmitter = self._transmitters_by_frequency.get(packet.frequency)
        if transmitter is None:
            return
        self._audio.play_encoded_audio(transmitter, packet.data, conflict)

    def _handle_connection_status(self, connected: bool):
        if connected:
            self._set_connection_state(ConnectionState.CONNECTED)
        else:
            self._set_connection_state(ConnectionState.DISCONNECTED)

    def clear(self):
        self._transmitters.clear()
        self._transmitters_by_frequency.clear()
        self._audio.cleanup()
        self._network.disconnect_from_server()

    def shutdown(self):
        self._network.shutdown()
        self._audio.shutdown()
