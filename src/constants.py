#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from pathlib import Path

from .utils.version import Version

config_version: Version = Version([1, 2, 0])
config_file: Path = Path.cwd() / "config.yaml"
app_version: Version = Version([1, 2, 0])
app_name: str = "AudioClient"
app_title: str = f"{app_name} v{app_version.version}"
version: bytes = f"{app_name}/{app_version.version}".encode("utf-8")

organization_name: str = "APOC Dev team"
organization_website: str = "https://www.apocfly.com"

# opus采样率，必须是12000的倍数
opus_default_sample_rate: int = 48000
# opus比特率
opus_default_bitrate: int = opus_default_sample_rate // 2
# 音频采样率
default_sample_rate: int = 44100
# 音频通道数
default_channels: int = 1
# 音频帧时长
default_frame_time: int = 20  # ms
default_frame_time_s: float = default_frame_time / 1000  # s
# 音频帧大小
default_frame_size: int = int(opus_default_sample_rate / (1000 / default_frame_time))
