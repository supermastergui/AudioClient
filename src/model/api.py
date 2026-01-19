#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from datetime import datetime
from typing import Generic, TypeVar

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
    solo_until: datetime
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
