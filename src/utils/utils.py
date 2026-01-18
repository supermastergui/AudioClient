#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

controller_list = ["DEL", "GND", "A_GND", "RMP", "TWR", "APP", "CTR", "FSS"]


def is_controller(callsign: str) -> bool:
    split = callsign.split('_')
    if len(split) == 1:
        return False
    suffix = split[-1].upper()
    return suffix in controller_list
