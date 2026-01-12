from typing import Callable, Optional

FrequencyChangeCallback = Callable[[int, int, bool], None]
ReceiveFlagCallback = Callable[[int, int, bool], None]


# 无线电台
class Transmitter:
    def __init__(self, frequency: int = 0, receive_flag: bool = False, transmitter_id: Optional[int] = None,
                 frequency_change_callback: Optional[FrequencyChangeCallback] = None,
                 receive_flag_change_callback: Optional[ReceiveFlagCallback] = None):
        self._transmitter_id = transmitter_id
        self._transmitter_frequency = frequency
        self._receive_flag = receive_flag
        self.frequency_change_callback = frequency_change_callback
        self.receive_flag_change_callback = receive_flag_change_callback

    @property
    def id(self) -> int:
        return self._transmitter_id

    @id.setter
    def id(self, transmitter_id: int):
        if transmitter_id is not None:
            raise ValueError("transmitter id cannot be set twice")
        self._transmitter_id = transmitter_id

    @property
    def frequency(self) -> int:
        return self._transmitter_frequency

    @frequency.setter
    def frequency(self, frequency: int):
        self._transmitter_frequency = frequency
        if self.frequency_change_callback is not None:
            self.frequency_change_callback(self._transmitter_id, frequency, self._receive_flag)

    @property
    def receive_flag(self) -> bool:
        return self._receive_flag

    @receive_flag.setter
    def receive_flag(self, receive_flag: bool):
        self._receive_flag = receive_flag
        if self.receive_flag_change_callback is not None:
            self.receive_flag_change_callback(self._transmitter_id, self._transmitter_frequency, receive_flag)
