#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from src.model import VersionType


class Version:
    def __init__(self, version: str | list[int]):
        if isinstance(version, str):
            version = version.split('.')
        self._major = int(version[0])
        self._minor = int(version[1])
        self._patch = int(version[2])

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    @property
    def patch(self) -> int:
        return self._patch

    @property
    def version(self) -> str:
        return f'{self._major}.{self._minor}.{self._patch}'

    def check_version(self, version: 'Version') -> VersionType:
        if self._major != version._major:
            return VersionType.MAJOR_UNMATCH
        if self._minor != version._minor:
            return VersionType.MINOR_UNMATCH
        if self._patch != version._patch:
            return VersionType.PATCH_UNMATCH
        return VersionType.ALL_MATCH

    def __str__(self) -> str:
        return self.version
