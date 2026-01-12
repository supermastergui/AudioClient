from typing import Optional

from loguru import logger
from numpy import int16, ndarray
from opuslib import APPLICATION_VOIP, Encoder

from src.constants import opus_default_bitrate, default_channels, default_frame_size, default_sample_rate


# Opus编码器
class OpusEncoder:
    def __init__(self,
                 sample_rate: int = default_sample_rate,
                 channels: int = default_channels,
                 frame_size: int = default_frame_size):
        self._sample_rate = sample_rate
        self._channels = channels
        self._frame_size = frame_size

        self._encoder = Encoder(sample_rate, channels, APPLICATION_VOIP)
        self._encoder.bitrate = opus_default_bitrate

    def encode(self, audio_data: ndarray) -> Optional[bytes]:
        try:
            if audio_data.dtype != int16:
                audio_data = audio_data.astype(int16) * 32767
            pcm_data = audio_data.tobytes()
            encoded_data = self._encoder.encode(pcm_data, self._frame_size)
            return encoded_data
        except Exception as e:
            logger.error(f"OPUS encoding error: {e}")
            return None

    @property
    def encoder(self) -> Encoder:
        return self._encoder

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def bitrate(self) -> int:
        return self._encoder.bitrate

    @bitrate.setter
    def bitrate(self, bitrate: int) -> None:
        try:
            self._encoder.bitrate = bitrate
        except Exception as e:
            logger.error(f"Failed to set bitrate: {e}")

    def __del__(self):
        if hasattr(self, "_encoder"):
            del self._encoder
            self._encoder = None
