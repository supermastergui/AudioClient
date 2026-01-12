from typing import Optional

from loguru import logger
from numpy import float32, frombuffer, int16, ndarray
from opuslib import Decoder

from src.constants import default_channels, default_frame_size, opus_default_sample_rate


# Opus解码器
class OpusDecoder:
    def __init__(self,
                 sample_rate: int = opus_default_sample_rate,
                 channels: int = default_channels,
                 frame_size: int = default_frame_size):
        self._sample_rate = sample_rate
        self._channels = channels
        self._frame_size = frame_size
        self._decoder = Decoder(sample_rate, channels)

    def decode(self, encoded_data: bytes) -> Optional[ndarray]:
        try:
            pcm_data = self._decoder.decode(encoded_data, self._frame_size)
            audio_data = frombuffer(pcm_data, dtype=int16)
            audio_data = audio_data.astype(float32) / 32768.0
            return audio_data
        except Exception as e:
            logger.error(f"OPUS decoding error: {e}")
            return None

    def __del__(self):
        if self._decoder is not None:
            del self._decoder
            self._decoder = None
