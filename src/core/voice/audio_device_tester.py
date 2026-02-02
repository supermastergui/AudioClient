#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from pyaudio import PyAudio

from src.signal import AudioClientSignals
from .opus import OpusDecoder, OpusEncoder, SteamArgs
from .stream import InputAudioSteam, OutputAudioSteam


class AudioDeviceTester:
    def __init__(self, signals: AudioClientSignals, audio: PyAudio, encoder: OpusEncoder, decoder: OpusDecoder):
        self._input_stream = InputAudioSteam(audio, encoder)
        self._output_stream = OutputAudioSteam(audio, decoder)
        self._input_stream.on_encoded_audio = self._on_encode_audio
        signals.ptt_status_change.connect(self._ptt_status_change)
        signals.microphone_gain_changed.connect(self._microphone_gain_change)

    def _microphone_gain_change(self, gain: int):
        self._input_stream.gain = gain

    def update_input_device(self, input_arg: SteamArgs):
        if self._input_stream.active:
            self._input_stream.restart(input_arg)

    def update_output_device(self, output_arg: SteamArgs):
        if self._output_stream.active:
            self._output_stream.restart(output_arg)

    def _ptt_status_change(self, status: bool):
        self._input_stream.input_active = status

    def _on_encode_audio(self, data: bytes):
        self._output_stream.play_encoded_audio(data)

    def start_test(self, input_arg: SteamArgs, output_arg: SteamArgs):
        self._input_stream.start(input_arg)
        self._output_stream.start(output_arg)

    def stop_test(self):
        self._input_stream.stop()
        self._output_stream.stop()
