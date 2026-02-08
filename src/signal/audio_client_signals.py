#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from PySide6.QtCore import QObject, Signal

from src.model import ConnectionState, ControlMessage, DeviceInfo, VoicePacket, WebSocketMessage


class AudioClientSignals(QObject):
    # emit when need to show config windows
    show_config_windows = Signal()
    # emit when login success
    login_success = Signal()
    # emit when request logout
    logout_request = Signal()
    # emit when broadcast message
    broadcast_message = Signal(WebSocketMessage)
    # emit to log message
    # arguments: from | level | content
    log_message = Signal(str, str, str)
    # emit when need show log message to user
    # arguments: from | level | content
    show_log_message = Signal(str, str, str)
    # emit when resize window
    # arguments: width | height | move to center
    resize_window = Signal(int, int, bool)

    # emit when connection changed
    connection_state_changed = Signal(ConnectionState)
    # emit when receive control message
    control_message_received = Signal(ControlMessage)
    # emit when receive voice data
    voice_data_received = Signal(VoicePacket)
    # emit when send voice data
    voice_data_sent = Signal()
    # emit when receive error
    error_occurred = Signal(str)
    # emit when frequency change
    update_current_frequency = Signal(int)

    # emit when request to show full window
    show_full_window = Signal()
    # emit when request to show small window
    show_small_window = Signal()

    # emit when test audio device
    test_audio_device = Signal(bool)
    # emit when microphone gain changed
    microphone_gain_changed = Signal(int)

    # emit when ptt press freq changed
    ptt_press_freq_changed = Signal(float)
    # emit when ptt release freq changed
    ptt_release_freq_changed = Signal(float)
    # emit when ptt volume changed
    ptt_volume_changed = Signal(float)

    # signals below are for internal use
    # emit when tcp and udp socket connect or disconnect
    socket_connection_state = Signal(bool)
    # emit when input device changed
    audio_input_device_change = Signal(DeviceInfo)
    # emit when output device changed
    audio_output_device_change = Signal(DeviceInfo)
    # emit when ptt button pressed or released
    ptt_status_change = Signal(bool)
    # emit when need to play ptt beep (True=press, False=release)
    ptt_beep = Signal(bool)
