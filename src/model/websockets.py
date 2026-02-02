#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from enum import Enum
from typing import Union

from pydantic import BaseModel


class BroadcastMessageType(Enum):
    kVoiceConnectedState = "kVoiceConnectedState"
    kStationStateUpdate = "kStationStateUpdate"
    kRxBegin = "kRxBegin"
    kRxEnd = "kRxEnd"
    kTxBegin = "kTxBegin"
    kTxEnd = "kTxEnd"


class StationStateUpdate(BaseModel):
    callsign: str
    frequency: int
    headset: bool
    rx: bool
    tx: bool
    xc: bool
    xca: bool
    isAvailable: bool
    isOutputMuted: bool
    outputVolume: int


class VoiceConnectedState(BaseModel):
    connected: bool


class RxBegin(BaseModel):
    callsign: str
    pFrequencyHz: int


class RxEnd(BaseModel):
    callsign: str
    pFrequencyHz: int


class WebSocketMessage(BaseModel):
    type: BroadcastMessageType
    value: Union[VoiceConnectedState, RxBegin, RxEnd]

    @staticmethod
    def voice_connected_state(connected: bool) -> 'WebSocketMessage':
        return WebSocketMessage(
            type=BroadcastMessageType.kVoiceConnectedState,
            value=VoiceConnectedState(connected=connected)
        )

    @staticmethod
    def rx_begin(callsign: str, frequency: int) -> 'WebSocketMessage':
        return WebSocketMessage(
            type=BroadcastMessageType.kRxBegin,
            value=RxBegin(callsign=callsign, pFrequencyHz=frequency)
        )

    @staticmethod
    def rx_end(callsign: str, frequency: int) -> 'WebSocketMessage':
        return WebSocketMessage(
            type=BroadcastMessageType.kRxEnd,
            value=RxEnd(callsign=callsign, pFrequencyHz=frequency)
        )
