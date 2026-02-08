#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT

from typing import Callable

from loguru import logger
from pydantic import BaseModel
from yaml import safe_dump, safe_load

from src.constants import config_file, config_version
from src.model import VersionType
from src.utils.version import Version


class LogConfig(BaseModel):
    level: str = "INFO"
    path: str = "logs/{time}.log"
    rotation: str = "1 day"
    retention: str = "14 days"
    compression: str = "zip"


class AccountConfig(BaseModel):
    username: str = ""
    password: str = ""
    remember_me: bool = False


class ServerConfig(BaseModel):
    api_endpoint: str = "http://127.0.0.1:6810"
    voice_endpoint: str = "127.0.0.1"
    voice_tcp_port: int = 6808
    voice_udp_port: int = 6807


class AudioConfig(BaseModel):
    api_driver: str = "自动"
    input_device: str = "默认"
    output_device: str = "默认"
    output_device_speaker: str = "默认"
    microphone_gain: int = 0
    ptt_key: str = "Key.ctrl_r"
    ptt_press_freq: float = 1500.0
    ptt_release_freq: float = 1000.0
    ptt_volume: float = 1.0
    conflict_volume: float = 1.0


class Config(BaseModel):
    version: str = config_version.version
    log: LogConfig = LogConfig()
    account: AccountConfig = AccountConfig()
    server: ServerConfig = ServerConfig()
    audio: AudioConfig = AudioConfig()

    @classmethod
    def load_config(cls) -> 'Config':
        if not config_file.exists():
            config_file.touch(mode=0o644)
            c = Config()
            with open(config_file, "w", encoding="utf-8") as f:
                safe_dump(c.model_dump(), f)
            return c
        with config_file.open("r", encoding="utf-8") as f:
            c = Config.model_validate(safe_load(f))
        return c


type SaveCallback = Callable[[], bool]


class ConfigManager:
    def __init__(self):
        self.config = Config.load_config()
        match config_version.check_version(Version(self.config.version)):
            case VersionType.MAJOR_UNMATCH | VersionType.MINOR_UNMATCH:
                logger.critical(f"Config > version error! Require {config_version} but got {self.config.version}")
                self.config.version = config_version.version
                self.save()
            case VersionType.PATCH_UNMATCH:
                logger.warning(f"Config > version not match! Require {config_version} but got {self.config.version}")
        self._save_callbacks: list[SaveCallback] = []

    def register_save_callback(self, callback: SaveCallback) -> None:
        self._save_callbacks.append(callback)

    def on_config_save(self, func: SaveCallback) -> SaveCallback:
        self.register_save_callback(func)
        logger.debug(f"Config > save callback {func.__name__} has been added")
        return func

    def save(self) -> None:
        result_list = [callback() for callback in self._save_callbacks]
        if not all(result_list):
            logger.error("Config > Some config save callback failed, rejecting save")
            logger.debug(
                f"Config > Failed callback list: {[callback for callback, result in zip(self._save_callbacks, result_list) if not result]}"
            )
            return
        with open(config_file, "w", encoding="utf-8") as f:
            safe_dump(self.config.model_dump(), f)


config_manager = ConfigManager()
config = config_manager.config
