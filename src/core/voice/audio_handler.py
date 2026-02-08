#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
"""
音频处理器：统一管理麦克风输入、耳机/扬声器双路混合输出、PTT 提示音、冲突音、设备测试与设备切换。
"""
from typing import Callable, Optional

from PySide6.QtCore import QTimer, Qt
from loguru import logger
from pyaudio import PyAudio

from src.config import config
from src.constants import default_channels, default_frame_size, default_frame_time, default_sample_rate, \
    opus_default_sample_rate
from src.model import DeviceInfo
from src.signal import AudioClientSignals
from .audio_device_tester import AudioDeviceTester
from .opus import OpusDecoder, OpusEncoder, SteamArgs
from .stream import InputAudioSteam, MixedOutputAudioStream
from .tone_generator import ToneGenerator
from .transmitter import Transmitter


class AudioHandler:
    """管理输入流、双路混合输出（耳机/扬声器）、PTT 提示音、冲突音音量、设备测试；按 transmitter.output_target 路由播放。"""

    def __init__(self, audio_signal: AudioClientSignals):
        self._input_args = SteamArgs(default_sample_rate, default_channels, None, default_frame_size)
        self._output_args = SteamArgs(default_sample_rate, default_channels, None, default_frame_size)
        self._output_args_speaker = SteamArgs(default_sample_rate, default_channels, None, default_frame_size)

        self._encoder = OpusEncoder(self._input_args)
        self._decoder = OpusDecoder(self._output_args)

        self._audio = PyAudio()
        self._input_stream = InputAudioSteam(self._audio, self._encoder)
        self._mixed_output_headphone = MixedOutputAudioStream(self._audio, self._decoder)
        self._mixed_output_speaker = MixedOutputAudioStream(self._audio, self._decoder)

        # 用于 PTT 提示音的专用 ToneGenerator（按下/松开各一个），
        # 在此处创建并在输出设备变更时更新采样率。
        self._ptt_press_tone = ToneGenerator(default_sample_rate, config.audio.ptt_press_freq, 0.3)
        self._ptt_release_tone = ToneGenerator(default_sample_rate, config.audio.ptt_release_freq, 0.3)
        self._beep_volume = config.audio.ptt_volume

        self._device_tester = AudioDeviceTester(audio_signal, self._audio, self._encoder, self._decoder)
        self._conflict_volume = config.audio.conflict_volume
        self._conflict_test_timer = QTimer()
        self._conflict_test_timer.setInterval(default_frame_time)
        self._conflict_test_timer.timeout.connect(
            lambda: self._device_tester.output_stream.play_conflict(self._conflict_volume)
        )

        self.audio_signal = audio_signal
        self.audio_signal.ptt_status_change.connect(self._ptt_status_change)
        self.audio_signal.ptt_beep.connect(self._ptt_beep)
        self.audio_signal.audio_input_device_change.connect(self._input_device_change)
        self.audio_signal.audio_output_device_change.connect(self._output_device_change)
        self.audio_signal.audio_output_device_speaker_change.connect(self._output_device_speaker_change)
        self.audio_signal.test_audio_device.connect(self._test_audio_device, Qt.ConnectionType.QueuedConnection)
        self.audio_signal.microphone_gain_changed.connect(self._microphone_gain_change)
        self.audio_signal.ptt_press_freq_changed.connect(
            lambda freq: self._ptt_press_tone.update_frequency(freq)
        )
        self.audio_signal.ptt_release_freq_changed.connect(
            lambda freq: self._ptt_release_tone.update_frequency(freq)
        )
        self.audio_signal.ptt_volume_changed.connect(self.ptt_beep_volume_change)
        self.audio_signal.conflict_volume_changed.connect(self._conflict_volume_change)

    def ptt_beep_volume_change(self, volume: float):
        self._beep_volume = volume

    def _conflict_volume_change(self, volume: float):
        self._conflict_volume = volume

    @property
    def on_encoded_audio(self) -> Optional[Callable[[bytes], None]]:
        return self._input_stream.on_encoded_audio

    @on_encoded_audio.setter
    def on_encoded_audio(self, on_encoded_audio: Callable[[bytes], None]):
        self._input_stream.on_encoded_audio = on_encoded_audio

    def _microphone_gain_change(self, gain: int):
        self._input_stream.gain = gain

    def _ptt_status_change(self, status: bool):
        self._input_stream.input_active = status

    def _ptt_beep(self, pressed: bool) -> None:
        tone = self._ptt_press_tone if pressed else self._ptt_release_tone
        if self._device_tester.active:
            wave = tone.generate_frame(self._device_tester.output_stream.frame_size) * 0.5 * self._beep_volume
            self._device_tester.output_stream.enqueue_conflict_wave(wave)
            return
        wave = tone.generate_frame(self._mixed_output_headphone.frame_size) * 0.5 * self._beep_volume
        self._mixed_output_headphone.enqueue_conflict_wave(wave)

    def _test_audio_device(self, state: bool, target: str):
        if state:
            if self._device_tester.active:
                self._device_tester.stop()
            if target == "headphone" or target == "conflict":
                self._device_tester.start(self._input_args, self._output_args)
            else:
                self._device_tester.start(self._input_args, self._output_args_speaker)
            if target == "conflict":
                self._conflict_test_timer.start()
        else:
            if self._device_tester.active:
                self._device_tester.stop()
            if self._conflict_test_timer.isActive():
                self._conflict_test_timer.stop()

    def _input_device_change(self, info: Optional[DeviceInfo]):
        if info is None:
            info = DeviceInfo.model_validate(self._audio.get_default_input_device_info())
        logger.debug(f"AudioHandler > input device change: {info}")
        self._input_args.device_index = info.index
        self._input_args.channel = max(info.maxInputChannels // 2, default_channels)
        self._input_args.sample_rate = int(info.defaultSampleRate)
        self._input_args.frame_size = int(
            default_frame_size * self._input_args.sample_rate / opus_default_sample_rate
        ) * self._input_args.channel
        self._encoder.update(self._input_args)
        self._device_tester.update_input_device(self._input_args)
        if not self._input_stream.active:
            return
        self._input_stream.restart(self._input_args)

    def _output_device_change(self, info: Optional[DeviceInfo]):
        if info is None:
            info = DeviceInfo.model_validate(self._audio.get_default_output_device_info())
        logger.debug(f"AudioHandler > output device (headphone) change: {info}")
        self._output_args.device_index = info.index
        self._output_args.channel = max(info.maxOutputChannels // 2, default_channels)
        self._output_args.sample_rate = int(info.defaultSampleRate)
        self._output_args.frame_size = int(
            default_frame_size * self._output_args.sample_rate / opus_default_sample_rate
        ) * self._input_args.channel
        self._decoder.update(self._output_args)
        self._ptt_press_tone.update_sample_rate(self._output_args.sample_rate)
        self._ptt_release_tone.update_sample_rate(self._output_args.sample_rate)
        self._device_tester.update_output_device(self._output_args)
        if self._mixed_output_headphone.active:
            self._mixed_output_headphone.restart(self._output_args)
        if self._mixed_output_speaker.active:
            self._mixed_output_speaker.restart(self._output_args_speaker)

    def _output_device_speaker_change(self, info: Optional[DeviceInfo]):
        if info is None:
            info = DeviceInfo.model_validate(self._audio.get_default_output_device_info())
        logger.debug(f"AudioHandler > output device (speaker) change: {info}")
        self._output_args_speaker.device_index = info.index
        self._output_args_speaker.channel = max(info.maxOutputChannels // 2, default_channels)
        self._output_args_speaker.sample_rate = int(info.defaultSampleRate)
        self._output_args_speaker.frame_size = int(
            default_frame_size * self._output_args_speaker.sample_rate / opus_default_sample_rate
        ) * self._output_args_speaker.channel
        if self._mixed_output_speaker.active:
            self._mixed_output_speaker.restart(self._output_args_speaker)

    def _stream_for_target(self, output_target: str) -> MixedOutputAudioStream:
        """按输出目标返回对应混合流。"""
        return self._mixed_output_headphone if output_target == "headphone" else self._mixed_output_speaker

    def add_transmitter(self, transmitter: Transmitter):
        stream = self._stream_for_target(transmitter.output_target)
        stream.add_transmitter(transmitter.id)
        logger.debug(f"AudioHandler > transmitter added: {transmitter}")

    def set_transmitter_output_target(self, transmitter: Transmitter) -> None:
        """将 transmitter 从当前输出切到另一路（耳机/扬声器）。"""
        old_stream = self._stream_for_target(
            "speaker" if transmitter.output_target == "headphone" else "headphone"
        )
        new_stream = self._stream_for_target(transmitter.output_target)
        old_stream.remove_transmitter(transmitter.id)
        new_stream.add_transmitter(transmitter.id)
        logger.debug(f"AudioHandler > transmitter {transmitter.id} switched to {transmitter.output_target}")

    def play_encoded_audio(self, transmitter: Transmitter, encoded_data: bytes, conflict: bool = False):
        if transmitter.volume == 0 or not transmitter.receive_flag:
            return
        volume = self._conflict_volume if conflict else transmitter.volume
        stream = self._stream_for_target(transmitter.output_target)
        stream.play_encoded_audio(
            transmitter.id, encoded_data, conflict, volume
        )

    def start(self):
        self._input_stream.start(self._input_args)
        self._mixed_output_headphone.start(self._output_args)
        self._mixed_output_speaker.start(self._output_args_speaker)

    def cleanup(self):
        self._input_stream.stop()
        self._mixed_output_headphone.stop()
        self._mixed_output_speaker.stop()

    def shutdown(self):
        self.cleanup()
        self._audio.terminate()
