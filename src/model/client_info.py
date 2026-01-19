#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
from typing import Optional

from .api import UserModel


# 客户端信息
class ClientInfo:
    def __init__(self):
        self.cid = 0
        self.callsign = ""
        self.jwt_token = ""
        self.flush_token = ""
        self.main_frequency = 0
        self.is_atc = False
        self.user: Optional[UserModel] = None

    def clear(self) -> None:
        self.callsign = ""
        self.main_frequency = 0
        self.is_atc = False

    def reset(self):
        self.clear()
        self.cid = 0
        self.jwt_token = ""
        self.flush_token = ""
        self.user = None

    @property
    def client_valid(self) -> bool:
        return self.cid != 0 and self.callsign != ""
