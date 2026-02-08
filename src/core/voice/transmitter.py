#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT


# 无线电台
class Transmitter:
    def __init__(self, frequency: int, transmitter_id: int, *, tx: bool = False, rx: bool = False, volume: float = 1.0):
        self.id = transmitter_id
        self.frequency = frequency
        self.send_flag = tx
        self.receive_flag = rx
        self.volume = volume

    def clear(self):
        self.send_flag = False
        self.receive_flag = False

    def __repr__(self) -> str:
        return f"<Transmitter id={self.id} frequency={self.frequency} send_flag={self.send_flag} receive_flag={self.receive_flag}>"
