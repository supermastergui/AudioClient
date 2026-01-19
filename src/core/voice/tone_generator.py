#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT

from numpy import pi, sin, float32, ndarray, zeros, arange
from numpy.typing import NDArray


class ToneGenerator:
    """
    正弦波生成器
    """

    def __init__(self, sample_rate: int = 44100, frequency: float = 293.66, amplitude: float = 0.3):
        self.sample_rate = sample_rate
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase_increment: float = 0.0
        self.samples_per_cycle = 0
        self.cycle_waveform: NDArray[float32] = zeros(0, dtype=float32)
        self.phase_pointer = 0
        self._precalculate_waveform()

    def update_arguments(self, sample_rate: int = 44100, frequency: float = 293.66, amplitude: float = 0.3):
        self.sample_rate = sample_rate
        self.frequency = frequency
        self.amplitude = amplitude
        self._precalculate_waveform()

    def _precalculate_waveform(self):
        # 预计算一个周期的波形
        self.phase_increment = 2 * pi * self.frequency / self.sample_rate
        self.samples_per_cycle = int(self.sample_rate / self.frequency)

        # 预计算一个完整周期的正弦波
        n = arange(self.samples_per_cycle) * self.phase_increment
        self.cycle_waveform = self.amplitude * sin(n).astype(float32)

        # 相位指针（在预计算波形中的位置）
        self.phase_pointer = 0

    def generate_frame(self, frame_size: int) -> NDArray[float32]:
        frame = zeros(frame_size, dtype=float32)

        # 从预计算波形中复制数据
        remaining = frame_size
        dest_pos = 0

        while remaining > 0:
            # 计算可以从当前相位指针复制的数量
            available = self.samples_per_cycle - self.phase_pointer

            if available >= remaining:
                # 可以一次复制完
                frame[dest_pos:dest_pos + remaining] = self.cycle_waveform[
                                                       self.phase_pointer:self.phase_pointer + remaining]
                self.phase_pointer += remaining
                break
            else:
                # 复制当前周期剩余部分
                frame[dest_pos:dest_pos + available] = self.cycle_waveform[
                                                       self.phase_pointer:self.phase_pointer + available]
                dest_pos += available
                remaining -= available
                # 重置相位指针到周期开始
                self.phase_pointer = 0

        # 确保相位指针在有效范围内
        self.phase_pointer %= self.samples_per_cycle

        return frame
