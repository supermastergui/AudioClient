#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from enum import Enum


class VersionType(Enum):
    ALL_MATCH = 0
    PATCH_UNMATCH = 1
    MINOR_UNMATCH = 2
    MAJOR_UNMATCH = 3
