#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from typing import Callable, Optional

from pyaudio import PyAudio

from src.constants import default_channels, default_frame_size, default_sample_rate, opus_default_sample_rate
from src.signal import AudioClientSignals
from .opus import OpusDecoder, OpusEncoder, SteamArgs
from .stream import InputAudioSteam, OutputAudioSteam
from .transmitter import Transmitter
from ...model import DeviceInfo


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

        self.audio_signal = audio_signal
        self.audio_signal.ptt_status_change.connect(self._ptt_status_change)
        self.audio_signal.audio_input_device_change.connect(self._input_device_change)
        self.audio_signal.audio_output_device_change.connect(self._output_device_change)

    @property
    def on_encoded_audio(self) -> Optional[Callable[[bytes], None]]:
        return self._input_stream.on_encoded_audio

    @on_encoded_audio.setter
    def on_encoded_audio(self, on_encoded_audio: Optional[Callable[[bytes], None]]):
        self._input_stream.on_encoded_audio = on_encoded_audio

    def _ptt_status_change(self, status: bool):
        self._input_stream.input_active = status

    def _input_device_change(self, index: int):
        if index != -1:
            data = self._audio.get_device_info_by_index(index)
        else:
            data = self._audio.get_default_input_device_info()
        info = DeviceInfo.model_validate(data)
        self._input_args.device_index = info.index
        self._input_args.channel = max(info.maxInputChannels // 2, default_channels)
        self._input_args.sample_rate = int(info.defaultSampleRate)
        self._input_args.frame_size = int(
            default_frame_size * self._input_args.sample_rate / opus_default_sample_rate
        ) * self._input_args.channel
        self._encoder.update(self._input_args)
        if not self._input_stream.active:
            return
        self._input_stream.restart(self._input_args)

    def _output_device_change(self, index: int):
        if index != -1:
            data = self._audio.get_device_info_by_index(index)
        else:
            data = self._audio.get_default_output_device_info()
        info = DeviceInfo.model_validate(data)
        self._output_args.channel = max(info.maxOutputChannels // 2, default_channels)
        self._output_args.sample_rate = int(info.defaultSampleRate)
        self._output_args.frame_size = int(
            default_frame_size * self._output_args.sample_rate / opus_default_sample_rate
        ) * self._input_args.channel
        self._decoder.update(self._output_args)
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
