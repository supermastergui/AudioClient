#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT


# 无线电台
class Transmitter:
    def __init__(self, frequency: int, transmitter_id: int, *, tx: bool = False, rx: bool = False):
        self._transmitter_id = transmitter_id
        self._transmitter_frequency = frequency
        self._send_flag = tx
        self._receive_flag = rx

    @property
    def id(self) -> int:
        return self._transmitter_id

    @property
    def frequency(self) -> int:
        return self._transmitter_frequency

    @frequency.setter
    def frequency(self, frequency: int):
        self._transmitter_frequency = frequency

    @property
    def receive_flag(self) -> bool:
        return self._receive_flag

    @receive_flag.setter
    def receive_flag(self, receive_flag: bool):
        self._receive_flag = receive_flag

    @property
    def send_flag(self) -> bool:
        return self._send_flag

    @send_flag.setter
    def send_flag(self, send_flag: bool):
        self._send_flag = send_flag

    def clear(self):
        self._send_flag = False
        self._receive_flag = False
