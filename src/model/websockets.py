#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


class WebSocketMessageItem(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        raise NotImplementedError


T = TypeVar("T", bound=WebSocketMessageItem)


class WebSocketMessage(Generic[T]):
    type: str
    value: T

    def __init__(self, value: T):
        self.type = value.get_type()
        self.value = value

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "value": self.value.to_dict()
        }


@dataclass
class VoiceConnectedState(WebSocketMessageItem):
    connected: bool

    def to_dict(self) -> dict:
        return {'connected': self.connected}

    @classmethod
    def get_type(cls) -> str:
        return "kVoiceConnectedState"


@dataclass
class RxBegin(WebSocketMessageItem):
    activeTransmitters: list[str]
    callsign: str
    pFrequencyHz: int

    def to_dict(self) -> dict:
        return {
            "activeTransmitters": self.activeTransmitters,
            "callsign": self.callsign,
            "pFrequencyHz": self.pFrequencyHz,
        }

    @classmethod
    def get_type(cls) -> str:
        return "kRxBegin"


@dataclass
class RxEnd(WebSocketMessageItem):
    activeTransmitters: list[str]
    callsign: str
    pFrequencyHz: int

    def to_dict(self) -> dict:
        return {
            "activeTransmitters": self.activeTransmitters,
            "callsign": self.callsign,
            "pFrequencyHz": self.pFrequencyHz,
        }

    @classmethod
    def get_type(cls) -> str:
        return "kRxEnd"
