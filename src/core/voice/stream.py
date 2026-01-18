#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from queue import Empty, Full, Queue
from typing import Callable, Optional

from loguru import logger
from numpy import float32, frombuffer, int16, zeros
from pyaudio import PyAudio, Stream, paContinue, paFloat32, paInt16
from soxr import resample  # type: ignore

from src.constants import default_sample_rate, opus_default_sample_rate
from .opus import OpusDecoder, OpusEncoder, SteamArgs


class AudioStream(ABC):
    def __init__(self, audio: PyAudio):
        self._audio = audio
        self._stream: Optional[Stream] = None
        self._active = False
        self._sample_rate = default_sample_rate

    @abstractmethod
    def start(self, args: SteamArgs):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    @property
    def active(self) -> bool:
        return self._active

    def restart(self, args: SteamArgs):
        self.stop()
        self.start(args)


class InputAudioSteam(AudioStream):
    def __init__(self, audio: PyAudio, encoder: OpusEncoder,
                 on_encoded_audio: Optional[Callable[[bytes], None]] = None):
        super().__init__(audio)
        self._input_active = False
        self._encoder = encoder
        self._on_encoded_audio: Optional[Callable[[bytes], None]] = on_encoded_audio

    @property
    def input_active(self) -> bool:
        return self._input_active

    @input_active.setter
    def input_active(self, input_active: bool):
        self._input_active = input_active

    @property
    def on_encoded_audio(self) -> Optional[Callable[[bytes], None]]:
        return self._on_encoded_audio

    @on_encoded_audio.setter
    def on_encoded_audio(self, on_encoded_audio: Optional[Callable[[bytes], None]]):
        self._on_encoded_audio = on_encoded_audio

    def _callback(self, in_data, _, __, ___):
        if self._input_active and self._on_encoded_audio:
            audio_data = frombuffer(in_data, dtype=int16)
            # 重采样麦克风输入的音频
            # 麦克风输入的采样率通常为44100Hz
            # OPUS编码的音频采样率通常为48000Hz
            resampled_audio = resample(audio_data, self._sample_rate, opus_default_sample_rate)
            if len(resampled_audio) == 0:
                logger.warning("empty data")
                return None, paContinue
            encoded_data = self._encoder.encode(resampled_audio)
            if encoded_data:
                self._on_encoded_audio(encoded_data)
        return None, paContinue

    def start(self, args: SteamArgs):
        if self._active:
            return
        self._sample_rate = args.sample_rate
        try:
            self._stream = self._audio.open(
                format=paInt16,
                channels=args.channel,
                rate=args.sample_rate,
                input=True,
                input_device_index=args.device_index,
                frames_per_buffer=args.frame_size,
                stream_callback=self._callback
            )
            self._active = True
            self._stream.start_stream()
            logger.info("Started audio recording")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")

    def stop(self):
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        self._active = False
        logger.info("Stopped audio recording")


class OutputAudioSteam(AudioStream):
    def __init__(self, audio: PyAudio, decoder: OpusDecoder):
        super().__init__(audio)
        self._decoder = decoder
        self._queue = Queue()

    def play_encoded_audio(self, encoded_data: bytes):
        try:
            self._queue.put_nowait(encoded_data)
        except Full:
            logger.warning("Output queue full, dropping audio packet")

    def _callback(self, _, frame_count: int, __, ___):
        try:
            encoded_data = self._queue.get_nowait()
            audio_data = self._decoder.decode(encoded_data)
            if audio_data is not None:
                # 重采样解码出来的音频数据
                # OPUS编码的音频采样率通常为48000Hz
                # 音频输出的采样率通常为44100Hz
                resampled_audio = resample(audio_data, opus_default_sample_rate, self._sample_rate)
                if resampled_audio.size != frame_count:
                    logger.warning(f"Resampling audio with {frame_count} frames")
                output_data = resampled_audio.astype(float32).tobytes()
                return output_data, paContinue
        except Empty:
            pass
        silence = zeros(frame_count, dtype=float32).tobytes()
        return silence, paContinue

    def start(self, args: SteamArgs):
        if self._active:
            return
        self._sample_rate = args.sample_rate
        try:
            self._stream = self._audio.open(
                format=paFloat32,
                channels=args.channel,
                rate=args.sample_rate,
                output=True,
                output_device_index=args.device_index,
                frames_per_buffer=args.frame_size,
                stream_callback=self._callback
            )
            self._active = True
            self._stream.start_stream()
            logger.info("Started audio playback")
        except Exception as e:
            logger.error(f"Failed to start playback: {e}")

    def stop(self):
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        self._active = False
        logger.info("Stopped audio playback")
