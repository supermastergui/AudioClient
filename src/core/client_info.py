#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

# 客户端信息
class ClientInfo:
    def __init__(self):
        self.cid = 0
        self.callsign = ""
        self.jwt_token = ""
        self.main_frequency = 0
        self.is_atc = False

    def clear(self) -> None:
        self.cid = 0
        self.callsign = ""
        self.main_frequency = 0
        self.is_atc = False

    def reset(self):
        self.clear()
        self.jwt_token = ""

    @property
    def client_valid(self) -> bool:
        return self.cid != 0 and self.callsign != ""
