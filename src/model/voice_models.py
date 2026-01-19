#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from dataclasses import dataclass
from enum import Enum
from struct import pack

from pydantic import BaseModel


class MessageType(str, Enum):
    SWITCH = "channel"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    TEXT_RECEIVE = "text_receive"
    VOICE_RECEIVE = "voice_receive"
    MESSAGE = "message"
    DISCONNECT = "disconnect"


class ConnectionState(Enum):
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    AUTHENTICATING = 3
    READY = 4


class ControlMessage(BaseModel):
    type: MessageType
    cid: int = 0
    callsign: str = ""
    transmitter: int = 0
    data: str = ""


@dataclass
class VoicePacket:
    cid: int
    transmitter: int
    frequency: int
    callsign: str
    data: bytes


class VoicePacketBuilder:
    @staticmethod
    def build_packet(cid: int, transmitter: int, frequency: int, callsign: str, audio_data: bytes) -> bytes:
        callsign_bytes = callsign.encode('utf-8')
        callsign_len = len(callsign_bytes)

        if callsign_len >= 255:
            raise ValueError("Callsign too long")

        if frequency >= 200000:
            raise ValueError("Frequency too large")

        if transmitter >= 255:
            raise ValueError("Transmitter ID too large")

        packet = bytearray()
        packet.extend(pack('<i', cid))
        packet.extend(pack('<b', transmitter))
        packet.extend(pack('<i', frequency))
        packet.append(callsign_len)
        packet.extend(callsign_bytes)
        packet.extend(audio_data)
        packet.extend(b'\n')

        return bytes(packet)
