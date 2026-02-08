#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from pyaudio import PyAudio

from src.signal import AudioClientSignals
from .opus import OpusDecoder, OpusEncoder, SteamArgs
from .stream import InputAudioSteam, OutputAudioSteam


class AudioDeviceTester:
    def __init__(self, signals: AudioClientSignals, audio: PyAudio, encoder: OpusEncoder, decoder: OpusDecoder, /):
        super().__init__()
        self.active = False
        self.input_stream = InputAudioSteam(audio, encoder)
        self.output_stream = OutputAudioSteam(audio, decoder)
        self.input_stream.on_encoded_audio = self._on_encode_audio
        signals.ptt_status_change.connect(self._ptt_status_change)
        signals.microphone_gain_changed.connect(self._microphone_gain_change)

    def _microphone_gain_change(self, gain: int):
        self.input_stream.gain = gain

    def update_input_device(self, input_arg: SteamArgs):
        if self.input_stream.active:
            self.input_stream.restart(input_arg)

    def update_output_device(self, output_arg: SteamArgs):
        if self.output_stream.active:
            self.output_stream.restart(output_arg)

    def _ptt_status_change(self, status: bool):
        self.input_stream.input_active = status

    def _on_encode_audio(self, data: bytes):
        self.output_stream.play_encoded_audio(data)

    def start(self, input_arg: SteamArgs, output_arg: SteamArgs):
        self.active = True
        self.input_stream.start(input_arg)
        self.output_stream.start(output_arg)

    def stop(self):
        self.input_stream.stop()
        self.output_stream.stop()
        self.active = False
