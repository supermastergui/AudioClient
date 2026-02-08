#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
"""Opus 编解码与流参数：SteamArgs、OpusDecoder、OpusEncoder。"""

from dataclasses import dataclass
from typing import Optional

from loguru import logger
from numpy import float32, frombuffer, int16, ndarray
from opuslib import APPLICATION_VOIP, Decoder, Encoder  # type: ignore

from src.constants import default_frame_size, opus_default_bitrate, opus_default_sample_rate


@dataclass
class SteamArgs:
    """音频流参数：采样率、声道数、设备索引、帧大小。"""
    sample_rate: int
    channel: int
    device_index: Optional[int]
    frame_size: int


class OpusDecoder:
    def __init__(self, args: SteamArgs):
        self._frame_size: int = 0
        self._decoder: Optional[Decoder] = None
        self.update(args)
        logger.debug(f"OpusDecoder > OPUS decoder created with sample rate {opus_default_sample_rate} Hz, "
                     f"channels {args.channel}, frame size {self._frame_size}")

    def update(self, args: SteamArgs):
        self._frame_size = args.channel * default_frame_size
        self._decoder = Decoder(opus_default_sample_rate, args.channel)

    def decode(self, encoded_data: bytes) -> Optional[ndarray]:
        try:
            pcm_data = self._decoder.decode(encoded_data, self._frame_size)  # type: ignore
            audio_data = frombuffer(pcm_data, dtype=int16)
            audio_data = audio_data.astype(float32) / 32768.0  # type: ignore
            return audio_data
        except Exception as e:
            logger.error(f"OpusDecoder > OPUS decoding error: {e}")
            return None

    def __del__(self):
        if self._decoder is not None:
            del self._decoder
            self._decoder = None


class OpusEncoder:
    """Opus 编码器：将麦克风 PCM 编码为 Opus 字节流用于发送。"""

    def __init__(self, args: SteamArgs):
        self._frame_size: int = 0
        self._encoder: Optional[Encoder] = None
        self.update(args)
        logger.debug(f"OpusEncoder > OPUS encoder created with sample rate {opus_default_sample_rate} Hz, "
                     f"channels {args.channel}, frame size {self._frame_size}")

    def update(self, args: SteamArgs):
        self._frame_size = args.channel * default_frame_size

        self._encoder = Encoder(opus_default_sample_rate, args.channel, APPLICATION_VOIP)
        self._encoder.bitrate = opus_default_bitrate

    def encode(self, audio_data: ndarray) -> Optional[bytes]:
        try:
            if audio_data.dtype != int16:
                audio_data = audio_data.astype(int16) * 32767
            pcm_data = audio_data.tobytes()
            encoded_data = self._encoder.encode(pcm_data, self._frame_size)  # type: ignore
            return encoded_data
        except Exception as e:
            logger.error(f"OpusEncoder > OPUS encoding error: {e}")
            return None

    def __del__(self):
        if hasattr(self, "_encoder") and self._encoder is not None:
            del self._encoder
            self._encoder = None
