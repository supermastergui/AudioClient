#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
"""
音频流：麦克风输入流、单路输出流、多路混合输出流。
输入流编码为 Opus；输出流解码并可选重采样，支持冲突音/提示音插入。
"""
from abc import ABC, abstractmethod
from queue import Empty, Full, Queue
from typing import Callable, Optional

from loguru import logger
from numpy import float32, frombuffer, int16, tanh, zeros
from numpy.typing import NDArray
from pyaudio import PyAudio, Stream, paContinue, paFloat32, paInt16
from soxr import resample  # type: ignore

from src.config import config
from src.constants import default_sample_rate, opus_default_sample_rate
from .opus import OpusDecoder, OpusEncoder, SteamArgs
from .tone_generator import ToneGenerator


def _resample_to_output(
        audio_data: NDArray[float32],
        out_sample_rate: int,
        frame_size: int,
        volume: float,
) -> list[NDArray[float32]]:
    """将解码后的 PCM 重采样到输出采样率，并按 frame_size 切分为多帧，每帧乘以 volume。"""
    if audio_data.size == 0:
        return []
    resampled = resample(
        audio_data, opus_default_sample_rate, out_sample_rate
    ).astype(float32)
    resampled = (resampled * volume).clip(-1.0, 1.0)
    frames = []
    for i in range(0, resampled.size, frame_size):
        end = min(i + frame_size, resampled.size)
        chunk = zeros(frame_size, dtype=float32)
        chunk[: end - i] = resampled[i:end]
        frames.append(chunk)
    return frames


class AudioStream(ABC):
    """音频流基类：封装 PyAudio 流与 active 状态，子类实现 start/stop。"""

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
    """麦克风输入流：回调内重采样、增益后 Opus 编码，通过 on_encoded_audio 送出。"""

    def __init__(self, audio: PyAudio, encoder: OpusEncoder,
                 on_encoded_audio: Optional[Callable[[bytes], None]] = None):
        super().__init__(audio)
        self._input_active = False
        self._encoder = encoder
        self._on_encoded_audio: Optional[Callable[[bytes], None]] = on_encoded_audio
        self._gain = 0  # 默认0dB

    @property
    def gain(self) -> int:
        return self._gain

    @gain.setter
    def gain(self, gain: int):
        self._gain = gain

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
    def on_encoded_audio(self, on_encoded_audio: Callable[[bytes], None]):
        self._on_encoded_audio = on_encoded_audio

    def _callback(self, in_data, _, __, ___):
        if self._input_active and self._on_encoded_audio:
            audio_data = frombuffer(in_data, dtype=int16) * (10 ** (self._gain / 20))
            audio_data = audio_data.clip(-32768, 32767).astype(int16)
            # 重采样麦克风输入的音频
            # 麦克风输入的采样率通常为44100Hz
            # OPUS编码的音频采样率通常为48000Hz
            resampled_audio = resample(audio_data, self._sample_rate, opus_default_sample_rate)
            if len(resampled_audio) == 0:
                logger.debug("InputAudioSteam > got empty data from microphone, ignored")
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
            logger.debug("InputAudioSteam > started audio recording")
        except Exception as e:
            logger.error(f"InputAudioSteam > failed to start recording: {e}")

    def stop(self):
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        self._active = False
        logger.debug("InputAudioSteam > stopped audio recording")


class OutputAudioSteam(AudioStream):
    """单路播放流：队列接收编码数据或冲突波形，回调中解码/重采样后输出。"""

    def __init__(self, audio: PyAudio, decoder: OpusDecoder):
        super().__init__(audio)
        self._decoder = decoder
        self._queue: Queue[bytes] = Queue()
        self._conflict_queue: Queue[NDArray[float32]] = Queue()
        self._generator = ToneGenerator()
        self._frame_size = 0
        self._channel = 1
        self._volume = 1.0

    @property
    def frame_size(self) -> int:
        return self._frame_size

    def play_conflict(self, volume: float):
        try:
            self._conflict_queue.put_nowait(self._generator.generate_frame(self._frame_size) * self._volume * volume)
        except Full:
            return

    def enqueue_conflict_wave(self, wave: NDArray[float32]) -> None:
        """将一段已经生成好的浮点波形送入冲突队列播放。"""
        if not self._active or self._frame_size <= 0:
            return
        if wave.size == 0:
            return
        try:
            self._conflict_queue.put_nowait(wave.astype(float32))
        except Full:
            logger.debug("OutputAudioSteam > output conflict queue full, dropping beep")

    def play_encoded_audio(self, encoded_data: bytes, conflict: bool = False, volume: float = 1.0):
        """放入一帧编码数据或冲突音；冲突时仅播放冲突音。"""
        self._volume = volume
        if conflict:
            self.play_conflict(config.audio.conflict_volume)
            return
        try:
            self._queue.put_nowait(encoded_data)
        except Full:
            logger.debug("OutputAudioSteam > Output queue full, dropping audio packet")

    def _get_conflict_audio(self, sample_count: int) -> tuple[NDArray[float32], bool]:
        try:
            data = self._conflict_queue.get_nowait()
            n = data.size
            if n != sample_count:
                if n >= sample_count:
                    data = data[:sample_count].astype(float32)
                else:
                    out = zeros(sample_count, dtype=float32)
                    out[:n] = data
                    data = out
            return data, True
        except Empty:
            return zeros(0, dtype=float32), False

    def _get_audio(self, sample_count: int) -> tuple[NDArray[float32], bool]:
        try:
            encoded_data = self._queue.get_nowait()
            audio_data = self._decoder.decode(encoded_data)
            if audio_data is None:
                return zeros(0, dtype=float32), False
            # 重采样解码出来的音频数据
            # OPUS编码的音频采样率通常为48000Hz
            # 音频输出的采样率通常为44100Hz
            resampled_audio = resample(audio_data, opus_default_sample_rate, self._sample_rate)
            n = resampled_audio.size
            if n != sample_count:
                logger.warning(
                    f"OutputAudioSteam > unmatched resampled audio size, expect {sample_count} but got {n}"
                )
                if n > sample_count:
                    resampled_audio = resampled_audio[:sample_count].copy()
                else:
                    out = zeros(sample_count, dtype=float32)
                    out[:n] = resampled_audio
                    resampled_audio = out
            return resampled_audio.astype(float32), True
        except Empty:
            return zeros(0, dtype=float32), False

    def _callback(self, _, frame_count: int, __, ___) -> tuple[bytes, int]:
        # PyAudio 的 frame_count 为帧数，每帧含 channel 个样本，需返回 frame_count * channel 个样本
        sample_count = frame_count * self._channel
        data, success = self._get_conflict_audio(sample_count)
        if success:
            return (data * self._volume).clip(-1.0, 1.0).tobytes(), paContinue
        data, success = self._get_audio(sample_count)
        if success:
            return (data * self._volume).clip(-1.0, 1.0).tobytes(), paContinue
        return zeros(sample_count, dtype=float32).tobytes(), paContinue

    def start(self, args: SteamArgs):
        if self._active:
            return
        self._generator.update_sample_rate(args.sample_rate)
        self._frame_size = args.frame_size
        self._channel = args.channel
        self._sample_rate = args.sample_rate
        try:
            self._stream = self._audio.open(
                format=paFloat32,
                channels=args.channel,
                rate=args.sample_rate,
                output=True,
                output_device_index=args.device_index,
                frames_per_buffer=args.frame_size // args.channel,
                stream_callback=self._callback
            )
            self._active = True
            self._stream.start_stream()
            logger.debug("OutputAudioSteam > started audio playback")
        except Exception as e:
            logger.error(f"Failed to start playback: {e}")

    def stop(self):
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        self._active = False
        logger.debug("OutputAudioSteam > stopped audio playback")


class MixedOutputAudioStream(AudioStream):
    """
    单设备混合输出：将多个 transmitter 的 PCM 按帧叠加后输出到同一设备。
    解码在调用线程完成，每路一个队列存放已解码且重采样后的 float32 帧。
    """

    def __init__(self, audio: PyAudio, decoder: OpusDecoder):
        super().__init__(audio)
        self._decoder = decoder
        self._transmitter_queues: dict[int, Queue[NDArray[float32]]] = {}
        self._conflict_queue: Queue[NDArray[float32]] = Queue()
        self._generator = ToneGenerator()
        self._frame_size = 0
        self._channel = 1
        self._sample_rate = default_sample_rate
        self._stream: Optional[Stream] = None

    @property
    def frame_size(self) -> int:
        return self._frame_size

    def add_transmitter(self, transmitter_id: int) -> None:
        """为该发射机分配一路队列。"""
        if transmitter_id not in self._transmitter_queues:
            self._transmitter_queues[transmitter_id] = Queue()

    def remove_transmitter(self, transmitter_id: int) -> None:
        """移除该发射机的队列（切换输出设备时用）。"""
        self._transmitter_queues.pop(transmitter_id, None)

    def enqueue_conflict_wave(self, wave: NDArray[float32]) -> None:
        if not self._active or self._frame_size <= 0 or wave.size == 0:
            return
        try:
            self._conflict_queue.put_nowait(wave.astype(float32))
        except Full:
            logger.debug("MixedOutputAudioStream > mixed output conflict queue full, dropping")

    def play_encoded_audio(self, transmitter_id: int, encoded_data: bytes,
                           conflict: bool = False, volume: float = 1.0) -> None:
        """将一帧数据送入对应 transmitter 队列；冲突时生成冲突音送入冲突队列。"""
        if not self._active or self._frame_size <= 0:
            return
        if conflict:
            try:
                frame = self._generator.generate_frame(self._frame_size) * volume
                self._conflict_queue.put_nowait(frame.astype(float32))
            except Full:
                logger.debug("MixedOutputAudioStream > mixed output conflict queue full, dropping")
            return
        if transmitter_id not in self._transmitter_queues:
            logger.trace(f"MixedOutputAudioStream > transmitter {transmitter_id} not in queue, dropping")
            return
        audio_data = self._decoder.decode(encoded_data)
        if audio_data is None:
            return
        for frame in _resample_to_output(audio_data, self._sample_rate, self._frame_size, volume):
            try:
                self._transmitter_queues[transmitter_id].put_nowait(frame)
            except Full:
                logger.debug(f"MixedOutputAudioStream >  transmitter {transmitter_id} queue full, dropping frame")

    def _get_conflict_audio(self, frame_count: int) -> tuple[NDArray[float32], bool]:
        """取一帧冲突音，不足或超出 frame_count 时补零或截断。"""
        try:
            data = self._conflict_queue.get_nowait()
            n = data.size
            if n != frame_count:
                logger.warning(
                    f"MixedOutputAudioStream > conflict audio size mismatch, expect {frame_count} but got {n}"
                )
                if n >= frame_count:
                    data = data[:frame_count].astype(float32)
                else:
                    out = zeros(frame_count, dtype=float32)
                    out[:n] = data.astype(float32)
                    data = out
            return data, True
        except Empty:
            return zeros(0, dtype=float32), False

    def _mix_one_frame(self, frame_count: int) -> NDArray[float32]:
        """多路叠加后经 tanh 软限幅；每路帧与 frame_count 不一致时截断或补零。"""
        mixed = zeros(frame_count, dtype=float32)
        for q in self._transmitter_queues.values():
            try:
                frame = q.get_nowait()
                n = frame.size
                if n != frame_count:
                    logger.warning(
                        f"MixedOutputAudioStream > transmitter frame size mismatch, expect {frame_count} but got {n}"
                    )
                if n >= frame_count:
                    mixed += frame[:frame_count]
                elif n > 0:
                    mixed[:n] += frame.astype(float32)
            except Empty:
                pass
        return tanh(mixed).astype(float32)

    def _callback(self, _, frame_count: int, __, ___) -> tuple[bytes, int]:
        # PyAudio 的 frame_count 为帧数，每帧含 channel 个样本，需返回 frame_count * channel 个样本
        sample_count = frame_count * self._channel
        data, has_conflict = self._get_conflict_audio(sample_count)
        if has_conflict:
            return data.tobytes(), paContinue
        mixed = self._mix_one_frame(sample_count)
        return mixed.tobytes(), paContinue

    def start(self, args: SteamArgs):
        if self._active:
            return
        self._generator.update_sample_rate(args.sample_rate)
        self._frame_size = args.frame_size
        self._channel = args.channel
        self._sample_rate = args.sample_rate
        try:
            self._stream = self._audio.open(
                format=paFloat32,
                channels=args.channel,
                rate=args.sample_rate,
                output=True,
                output_device_index=args.device_index,
                frames_per_buffer=args.frame_size // args.channel,
                stream_callback=self._callback,
            )
            self._active = True
            self._stream.start_stream()
            logger.debug("MixedOutputAudioStream > started mixed audio playback")
        except Exception as e:
            logger.error(f"Failed to start mixed playback: {e}")

    def stop(self):
        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        self._active = False
        self._transmitter_queues.clear()
        logger.debug("MixedOutputAudioStream > stopped mixed audio playback")

    def restart(self, args: SteamArgs):
        self.stop()
        self.start(args)
