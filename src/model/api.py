#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from datetime import datetime
from typing import Generic, Mapping, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ApiResponse(BaseModel, Generic[T]):
    code: str
    message: str
    data: T


class UserModel(BaseModel):
    id: int
    cid: int
    username: str
    email: str
    avatar_url: str
    qq: int
    permission: int
    rating: int
    guest: bool
    tier2: bool
    under_monitor: bool
    under_solo: bool
    solo_until: Optional[datetime]
    total_atc_time: int
    total_pilot_time: int
    register_time: datetime


class UserLoginModel(BaseModel):
    user: UserModel
    token: str
    flush_token: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserLoginResponse(ApiResponse[UserLoginModel]):
    pass


class UserRefreshResponse(ApiResponse[UserLoginModel]):
    pass


class OnlinePilotModel(BaseModel):
    cid: int
    callsign: str
    real_name: str
    latitude: float
    longitude: float
    transponder: str
    pitch: float
    bank: float
    heading: float
    on_ground: bool
    voice_range: float
    altitude: int
    ground_speed: int
    flight_plan: Optional[Mapping[str, str | int | bool]]
    logon_time: str


class OnlineControllerModel(BaseModel):
    cid: int
    callsign: str
    real_name: str
    latitude: float
    longitude: float
    rating: int
    facility: int
    frequency: int
    range: int
    voice_range: int
    offline_time: str
    is_break: bool
    atc_info: list[str]
    logon_time: datetime


class OnlineGeneralModel(BaseModel):
    version: int
    generate_time: datetime
    connected_clients: int
    online_pilot: int
    online_controller: int


class OnlineClientsModel(BaseModel):
    general: OnlineGeneralModel
    pilots: list[OnlinePilotModel]
    controllers: list[OnlineControllerModel]
