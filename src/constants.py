#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from pathlib import Path

from .utils.version import Version

config_version: Version = Version([1, 2, 1])
config_file: Path = Path.cwd() / "config.yaml"
app_version: Version = Version([1, 2, 2])
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
# 音频通道数（输入/输出与 Opus 一致，Opus 仅支持 1 或 2 声道）
default_channels: int = 1
# 输出/输入流最大声道数，超过此值的设备按此值打开流，避免 Opus 与多声道设备不兼容
max_stream_channels: int = 2
# 音频帧时长
default_frame_time: int = 20  # ms
default_frame_time_s: float = default_frame_time / 1000  # s
# 音频帧大小
default_frame_size: int = int(opus_default_sample_rate / (1000 / default_frame_time))

# 会话保持：登录后后台刷新主 token 的间隔（分钟）
session_refresh_interval_minutes: int = 10
