#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from pydantic import BaseModel


class DeviceInfo(BaseModel):
    index: int
    structVersion: int
    name: str
    hostApi: int
    maxInputChannels: int
    maxOutputChannels: int
    defaultLowInputLatency: float
    defaultLowOutputLatency: float
    defaultHighInputLatency: float
    defaultHighOutputLatency: float
    defaultSampleRate: float
