#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
"""发射机模型：表示一个逻辑电台（频率、收发标志、音量、输出设备）。"""
from enum import Enum


# 输出目标：耳机 或 扬声器
class OutputTarget(Enum):
    Headphone = "headphone"
    Speaker = "speaker"


class Transmitter:
    """单个无线电台：频率、id、是否发送/接收、音量、输出到耳机或扬声器。"""

    def __init__(self, frequency: int, transmitter_id: int, *,
                 tx: bool = False, rx: bool = False, volume: float = 1.0,
                 output_target: OutputTarget = OutputTarget.Headphone):
        self.id = transmitter_id
        self.frequency = frequency
        self.send_flag = tx
        self.receive_flag = rx
        self.volume = volume
        self.output_target: OutputTarget = output_target

    def clear(self):
        """重置收发标志。"""
        self.send_flag = False
        self.receive_flag = False

    def __repr__(self) -> str:
        return (f"<Transmitter id={self.id} frequency={self.frequency} "
                f"send_flag={self.send_flag} receive_flag={self.receive_flag} output={self.output_target}>")
