#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from time import time
from typing import Union

from PySide6.QtCore import QObject, QTimer
from loguru import logger

from src.model.voice_models import ConnectionState, ControlMessage, MessageType, VoicePacket, VoicePacketBuilder
from src.signal import AudioClientSignals
from src.core.voice.audio_handler import AudioHandler
from src.core.client_info import ClientInfo
from src.core.network_handler import NetworkHandler
from src.core.voice.transmitter import Transmitter
from src.constants import default_frame_time, default_frame_time_s


# 语音客户端
class VoiceClient(QObject):
    def __init__(self, client_info: ClientInfo, signals: AudioClientSignals):
        super().__init__()

        self._connection_state = ConnectionState.DISCONNECTED
        self._network = NetworkHandler(signals)
        self._audio = AudioHandler(signals)
        self.signals = signals
        self.client_info = client_info
        self.transmitters: dict[int, Transmitter] = {}
        self.receiving: dict[str, float] = {}
        self._current_transmitter = -1

        self._audio.on_encoded_audio = self._send_voice_data
        self.signals.control_message_received.connect(self._handle_control_message)
        self.signals.voice_data_received.connect(self._handle_voice_packet)
        self.signals.socket_connection_state.connect(self._handle_connection_status)
        self._thread_handler()

    def _thread_handler(self):
        def receiving_clean_handler():
            delete_keys = []
            current_time = time()
            for callsign, t in self.receiving.items():
                if current_time - t > default_frame_time_s:
                    delete_keys.append(callsign)
            for i in delete_keys:
                del self.receiving[i]

        clean_timer = QTimer()
        clean_timer.timeout.connect(receiving_clean_handler)
        clean_timer.setInterval(default_frame_time)
        clean_timer.start()

        def heartbeat_send_handler():
            if not self.client_ready:
                return
            message = ControlMessage(type=MessageType.PING, cid=self.client_info.cid,
                                     callsign=self.client_info.callsign, data=str(int(time())))
            self._network.send_control_message(message)

        self._heartbeat_timer = QTimer()
        self._heartbeat_timer.timeout.connect(heartbeat_send_handler)
        self._heartbeat_timer.setInterval(15000)

    def _log_message(self, level: str, message: str):
        self.signals.log_message.emit("VoiceClient", level, message)

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
        self._current_transmitter = -1
        self._audio.cleanup()
        self.transmitters.clear()
        self.client_info.clear()

    def add_transmitter(self, transmitter: Transmitter):
        if transmitter.id is None:
            transmitter.id = len(self.transmitters.keys())
        self.transmitters[transmitter.id] = transmitter
        self.update_transmitter(transmitter)
        self._audio.add_transmitter(transmitter)
        self._init_transmitters(transmitter)

    def remove_transmitter(self, transmitter_id: int):
        del self.transmitters[transmitter_id]

    def update_transmitter(self, transmitter: Union[Transmitter, int]):
        if not self.client_ready:
            return

        if isinstance(transmitter, int):
            if transmitter >= len(self.transmitters):
                raise ValueError("Invalid transmitter id")
            transmitter = self.transmitters[transmitter]
        elif not isinstance(transmitter, Transmitter):
            raise ValueError("Invalid transmitter")

        frequency = transmitter.frequency
        rx = transmitter.receive_flag
        transmitter_id = transmitter.id

        if transmitter.send_flag:
            self.signals.update_current_frequency.emit(frequency)
            self._current_transmitter = transmitter_id

        message = ControlMessage(
            type=MessageType.SWITCH,
            cid=self.client_info.cid,
            callsign=self.client_info.callsign,
            transmitter=transmitter_id,
            data=f"{frequency}:{'1' if rx else '0'}"
        )
        self._log_message("INFO", f"Switch transmitter {transmitter} to {frequency / 1000:.3f}mHz receive flag {rx}")
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

    def _init_transmitters(self, transmitter: Transmitter):
        packet = VoicePacketBuilder.build_packet(self.client_info.cid,
                                                 transmitter.id,
                                                 transmitter.frequency,
                                                 self.client_info.callsign,
                                                 b"")
        self._network.send_voice_packet(packet)

    def _send_voice_data(self, encoded_data: bytes):
        if not self.client_ready or self._current_transmitter == -1:
            return

        transmitter = self.transmitters.get(self._current_transmitter, None)
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
            logger.error(f"Server error: {message.data}")
            self.signals.error_occurred.emit(message.data)
        elif message.type == MessageType.PONG:
            logger.debug("Received pong from server")
        elif message.type == MessageType.MESSAGE:
            if message.data.startswith("SERVER:"):
                if "Welcome" in message.data:
                    data = message.data.split(":")
                    self.client_info.callsign = data[1]
                    self._log_message("INFO", f"Starting heartbeat timer")
                    self._heartbeat_timer.start()
                    self._audio.start()
                    if len(data) == 4:
                        self.client_info.main_frequency = int(data[-1])
                        self.client_info.is_atc = True
                    self._set_connection_state(ConnectionState.READY)
                    self._log_message("INFO", "Identity verification passed")
        elif message.type == MessageType.DISCONNECT:
            self._heartbeat_timer.stop()
            self._audio.cleanup()
            self._network.disconnect_from_server()
            self._set_connection_state(ConnectionState.DISCONNECTED)

    def _handle_voice_packet(self, packet: VoicePacket):
        self.receiving[packet.callsign] = time()
        self._audio.play_encoded_audio(packet.transmitter, packet.data)

    def _handle_connection_status(self, connected: bool):
        if connected:
            self._set_connection_state(ConnectionState.CONNECTED)
        else:
            self._heartbeat_timer.stop()
            self._set_connection_state(ConnectionState.DISCONNECTED)
