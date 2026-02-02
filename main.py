#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

import sys
from time import time

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStyleFactory
from loguru import logger

from src.constants import app_name, app_version, organization_name, organization_website
from src.utils import QSSLoader


def log_message(source: str, level: str, content: str):
    logger.log(level, f"{source} > {content}")


def main() -> None:
    from src.utils.logger import logger_init
    logger_init()

    try:
        from opuslib.api import libopus  # type: ignore
    except FileNotFoundError:
        logger.critical("can't found opuslib")
    except OSError:
        logger.critical("can't load opuslib")

    start_time = time()
    last_time = start_time
    logger.info("Application initializing")
    logger.trace("Creating application")
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setApplicationName(app_name)
    app.setApplicationVersion(app_version.version)
    app.setOrganizationName(organization_name)
    app.setOrganizationDomain(organization_website)
    logger.trace(f"Create application cost {time() - last_time:.6f}s")

    last_time = time()
    logger.trace("Importing resource")
    import resource_rc
    app.setWindowIcon(QIcon(":/icon/icon"))
    app.setStyleSheet(QSSLoader.readQssResource(":/style/style/style.qss"))
    logger.trace(f"Import resource cost {time() - last_time:.6f}s")

    last_time = time()
    logger.trace("Creating main window")
    from src.ui.main_window import MainWindow
    from src.signal import AudioClientSignals, MouseSignals, KeyBoardSignals
    main_signals = AudioClientSignals()
    main_signals.log_message.connect(log_message)
    main_window = MainWindow(main_signals, MouseSignals(), KeyBoardSignals())
    logger.trace(f"Create main window cost {time() - last_time:.6f}s")

    logger.info(f"Startup completed in {time() - start_time:.6f}s")

    main_window.show()
    exit_code = app.exec()
    resource_rc.qCleanupResources()
    main_window.voice_client.shutdown()  # type: ignore
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
