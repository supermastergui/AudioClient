from queue import Empty, Full, Queue
from typing import Callable, Optional

from loguru import logger
from numpy import float32, frombuffer, int16, zeros
from pyaudio import PyAudio, Stream, paContinue, paFloat32, paInt16
from soxr import resample

from src.constants import default_channels, default_frame_size, default_sample_rate, opus_default_sample_rate
from src.signal import AudioClientSignals
from .codecs.opus_decoder import OpusDecoder
from .codecs.opus_encoder import OpusEncoder


# 音频处理器
# 捕获音频，使用Opus编码并输出
# 获取音频流，使用Opus解码并播放
class AudioHandler:
    def __init__(self, audio_signal: AudioClientSignals):
        self._input_sample_rate = default_sample_rate
        self._output_sample_rate = default_sample_rate

        self._input_channels = default_channels
        self._output_channels = default_channels
        self._frame_size = default_frame_size

        self._input_frame_size = int(default_frame_size * self._input_sample_rate / opus_default_sample_rate)
        self._output_frame_size = int(default_frame_size * self._output_sample_rate / opus_default_sample_rate)

        self._audio = PyAudio()
        self._input_stream: Optional[Stream] = None
        self._output_stream: Optional[Stream] = None

        self._encoder = OpusEncoder(opus_default_sample_rate, default_channels, default_frame_size)
        self._decoder = OpusDecoder(opus_default_sample_rate, default_channels, default_frame_size)

        self._output_queue = Queue()

        self._is_recording = False
        self._is_playing = False
        self._ptt_active = False
        self._input_device: Optional[int] = None
        self._output_device: Optional[int] = None

        self.on_encoded_audio: Optional[Callable] = None

        self.audio_signal = audio_signal
        self.audio_signal.ptt_status_change.connect(self._ptt_status_change)
        self.audio_signal.audio_input_device_change.connect(self._input_device_change)
        self.audio_signal.audio_output_device_change.connect(self._output_device_change)

    def _ptt_status_change(self, status: bool):
        self._ptt_active = status

    def _input_device_change(self, index: int):
        if index == -1:
            self._input_device = None
        else:
            self._input_device = index
        info = self._audio.get_device_info_by_index(index)
        self._input_channels = max(int(info["maxInputChannels"]) // 2, default_channels)
        self._input_sample_rate = int(info["defaultSampleRate"])
        self._input_frame_size = int(default_frame_size * self._input_sample_rate / opus_default_sample_rate)
        if self._is_recording:
            self.stop_recording()
            self.start_recording()

    def _output_device_change(self, index: int):
        if index == -1:
            self._output_device = None
        else:
            self._output_device = index
        info = self._audio.get_device_info_by_index(index)
        self._output_channels = max(int(info["maxOutputChannels"]) // 2, default_channels)
        self._output_sample_rate = int(info["defaultSampleRate"])
        self._output_frame_size = int(default_frame_size * self._output_sample_rate / opus_default_sample_rate)
        if self._is_playing:
            self.stop_playback()
            self.start_playback()

    def start_recording(self):
        if self._is_recording:
            return
        try:
            self._input_stream = self._audio.open(
                format=paInt16,
                channels=self._input_channels,
                rate=self._input_sample_rate,
                input=True,
                input_device_index=self._input_device,
                frames_per_buffer=self._input_frame_size,
                stream_callback=self._input_callback
            )
            self._is_recording = True
            self._input_stream.start_stream()
            logger.info("Started audio recording")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")

    def stop_recording(self):
        if self._input_stream:
            self._input_stream.stop_stream()
            self._input_stream.close()
            self._input_stream = None
        self._is_recording = False
        logger.info("Stopped audio recording")

    def start_playback(self):
        if self._is_playing:
            return
        try:
            self._output_stream = self._audio.open(
                format=paFloat32,
                channels=self._output_channels,
                rate=self._output_sample_rate,
                output=True,
                output_device_index=self._output_device,
                frames_per_buffer=self._output_frame_size,
                stream_callback=self._output_callback
            )
            self._is_playing = True
            self._output_stream.start_stream()
            logger.info("Started audio playback")
        except Exception as e:
            logger.error(f"Failed to start playback: {e}")

    def stop_playback(self):
        if self._output_stream:
            self._output_stream.stop_stream()
            self._output_stream.close()
            self._output_stream = None
        self._is_playing = False
        logger.info("Stopped audio playback")

    def _input_callback(self, in_data, _, __, ___):
        if self._ptt_active and self.on_encoded_audio:
            audio_data = frombuffer(in_data, dtype=int16)
            # 重采样麦克风输入的音频
            # 麦克风输入的采样率通常为44100Hz
            # OPUS编码的音频采样率通常为48000Hz
            resampled_audio = resample(audio_data, self._input_sample_rate, opus_default_sample_rate)
            if len(resampled_audio) == 0:
                logger.warning("empty data")
                return None, paContinue
            encoded_data = self._encoder.encode(resampled_audio)
            if encoded_data:
                self.on_encoded_audio(encoded_data)
        return None, paContinue

    def _output_callback(self, _, frame_count: int, __, ___):
        try:
            encoded_data = self._output_queue.get_nowait()
            audio_data = self._decoder.decode(encoded_data)
            if audio_data is not None:
                # 重采样解码出来的音频数据
                # OPUS编码的音频采样率通常为48000Hz
                # 音频输出的采样率通常为44100Hz
                resampled_audio = resample(audio_data, opus_default_sample_rate, self._output_sample_rate)
                if resampled_audio.size != frame_count:
                    logger.warning(f"Resampling audio with {frame_count} frames")
                output_data = resampled_audio.astype(float32).tobytes()
                return output_data, paContinue
        except Empty:
            pass
        silence = zeros(frame_count, dtype=float32).tobytes()
        return silence, paContinue

    def play_encoded_audio(self, encoded_data: bytes):
        try:
            self._output_queue.put_nowait(encoded_data)
        except Full:
            logger.warning("Output queue full, dropping audio packet")

    @property
    def ptt(self) -> bool:
        return self._ptt_active

    @ptt.setter
    def ptt(self, value: bool):
        self._ptt_active = value
        logger.trace(f"Set PTT state: {value}")

    def cleanup(self):
        self.stop_recording()
        self.stop_playback()
        self._audio.terminate()
