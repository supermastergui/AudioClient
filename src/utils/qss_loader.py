#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from PySide6.QtCore import QFile, QIODeviceBase, QTextStream


class QSSLoader:
    @staticmethod
    def readQssResource(resource_path: str) -> str:
        stream = QFile(resource_path)
        stream.open(QIODeviceBase.OpenModeFlag.ReadOnly)
        return QTextStream(stream).readAll()
