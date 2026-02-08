#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from typing import Callable, Optional

from loguru import logger
from pyaudio import PyAudio

from src.constants import default_channels, default_frame_size, default_sample_rate, opus_default_sample_rate
from src.model import DeviceInfo
from src.signal import AudioClientSignals
from .audio_device_tester import AudioDeviceTester
from .opus import OpusDecoder, OpusEncoder, SteamArgs
from .stream import InputAudioSteam, OutputAudioSteam
from .tone_generator import ToneGenerator
from .transmitter import Transmitter
from src.config import config


# 音频处理器
# 捕获音频，使用Opus编码并输出
# 获取音频流，使用Opus解码并播放
class AudioHandler:
    def __init__(self, audio_signal: AudioClientSignals):
        self._input_args: SteamArgs = SteamArgs(default_sample_rate, default_channels, None, default_frame_size)
        self._output_args: SteamArgs = SteamArgs(default_sample_rate, default_channels, None, default_frame_size)

        self._encoder = OpusEncoder(self._input_args)
        self._decoder = OpusDecoder(self._output_args)

        self._audio = PyAudio()
        self._input_stream = InputAudioSteam(self._audio, self._encoder)
        self._output_streams: dict[int, OutputAudioSteam] = {}

        # 用于 PTT 提示音的专用 ToneGenerator（按下/松开各一个），
        # 在此处创建并在输出设备变更时更新采样率。
        self._ptt_press_tone = ToneGenerator(default_sample_rate, config.audio.ptt_press_freq, 0.3)
        self._ptt_release_tone = ToneGenerator(default_sample_rate, config.audio.ptt_release_freq, 0.3)
        self._beep_volume = config.audio.ptt_volume

        self._device_tester = AudioDeviceTester(audio_signal, self._audio, self._encoder, self._decoder)

        self.audio_signal = audio_signal
        self.audio_signal.ptt_status_change.connect(self._ptt_status_change)
        self.audio_signal.ptt_beep.connect(self._ptt_beep)
        self.audio_signal.audio_input_device_change.connect(self._input_device_change)
        self.audio_signal.audio_output_device_change.connect(self._output_device_change)
        self.audio_signal.test_audio_device.connect(self._test_audio_device)
        self.audio_signal.microphone_gain_changed.connect(self._microphone_gain_change)
        self.audio_signal.ptt_press_freq_changed.connect(
            lambda freq: self._ptt_press_tone.update_frequency(freq)
        )
        self.audio_signal.ptt_release_freq_changed.connect(
            lambda freq: self._ptt_release_tone.update_frequency(freq)
        )
        self.audio_signal.ptt_volume_changed.connect(self.ptt_beep_volume_change)

    def ptt_beep_volume_change(self, volume: float):
        self._beep_volume = volume

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
        """
        在当前选定的输出设备上播放 PTT 提示音。

        所有已激活的输出流都会播放，以保持与接收音频相同的设备选择。
        """
        tone = self._ptt_press_tone if pressed else self._ptt_release_tone
        wave = tone.generate_frame(self._device_tester.output_stream.frame_size) * 0.5 * self._beep_volume
        self._device_tester.output_stream.enqueue_conflict_wave(wave)
        for stream in self._output_streams.values():
            if not stream.active or stream.frame_size <= 0:
                continue
            wave = tone.generate_frame(stream.frame_size)
            stream.enqueue_conflict_wave(wave)

    def _test_audio_device(self, state: bool):
        if state:
            self._device_tester.start_test(self._input_args, self._output_args)
        else:
            self._device_tester.stop_test()

    def _input_device_change(self, info: Optional[DeviceInfo]):
        if info is None:
            info = DeviceInfo.model_validate(self._audio.get_default_input_device_info())
        logger.info(f"input device change: {info}")
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
        logger.info(f"output device change: {info}")
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
        for stream in self._output_streams.values():
            if not stream.active:
                continue
            stream.restart(self._output_args)

    def add_transmitter(self, transmitter: Transmitter):
        self._output_streams[transmitter.id] = OutputAudioSteam(self._audio, self._decoder)
        self._output_streams[transmitter.id].start(self._output_args)

    def play_encoded_audio(self, transmitter: Transmitter, encoded_data: bytes, conflict: bool = False):
        stream = self._output_streams.get(transmitter.id, None)
        if stream is None:
            return
        if transmitter.volume == 0:
            return
        stream.play_encoded_audio(encoded_data, conflict, transmitter.volume)

    def start(self):
        self._input_stream.start(self._input_args)

    def cleanup(self):
        self._input_stream.stop()
        for stream in self._output_streams.values():
            stream.stop()
        self._output_streams.clear()

    def shutdown(self):
        self.cleanup()
        self._audio.terminate()
