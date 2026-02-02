#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from pydantic import BaseModel


class HostApiInfo(BaseModel):
    index: int
    structVersion: int
    type: int
    name: str
    deviceCount: int
    defaultInputDevice: int
    defaultOutputDevice: int


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

    def fix_name(self):
        try:
            name = self.name.encode("GBK").decode("utf8")
        except UnicodeEncodeError:
            pass
        except UnicodeDecodeError:
            pass
        else:
            self.name = name