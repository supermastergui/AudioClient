#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
"""登录保持：通过刷新 token 刷新主密钥。接口见 https://api.half-nothing.cn/343273543e0"""
from typing import Optional
from urllib.parse import urljoin

from loguru import logger

from src.config import config
from src.model import UserLoginModel, UserRefreshResponse
from src.utils import http


def refresh_session(flush_token: str) -> Optional[UserLoginModel]:
    """使用 flush_token 作为 Bearer 调用 GET /api/users/sessions 刷新会话，返回新 UserLoginModel；失败返回 None。"""
    if not flush_token:
        return None
    try:
        response = http.client.get(
            urljoin(config.server.api_endpoint, "/api/users/sessions"),
            headers={"Authorization": f"Bearer {flush_token}"},
        )
        if response.status_code != 200:
            logger.warning(f"auth > refresh failed status={response.status_code}")
            return None
        data = UserRefreshResponse.model_validate_json(response.content).data
        logger.debug("auth > session refreshed")
        return data
    except Exception as e:
        logger.warning(f"auth > refresh error: {e}")
        return None
