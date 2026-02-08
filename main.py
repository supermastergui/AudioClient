#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

import sys
from time import time

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStyleFactory
from loguru import logger

from src.constants import app_name, app_version, organization_name, organization_website
from src.utils import QSSLoader


def main() -> None:
    from src.utils.logger import logger_init
    logger_init()

    try:
        from opuslib.api import libopus  # type: ignore
    except FileNotFoundError:
        logger.critical("Main > can't found opuslib")
    except OSError:
        logger.critical("Main > can't load opuslib")

    start_time = time()
    last_time = start_time
    logger.debug("Main > application initializing")
    logger.trace("Main > creating application")
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setApplicationName(app_name)
    app.setApplicationVersion(app_version.version)
    app.setOrganizationName(organization_name)
    app.setOrganizationDomain(organization_website)
    logger.trace(f"Main > create application cost {time() - last_time:.6f}s")

    last_time = time()
    logger.debug("Main > importing resource")
    import resource_rc
    app.setWindowIcon(QIcon(":/icon/icon"))
    app.setStyleSheet(QSSLoader.readQssResource(":/style/style/style.qss"))
    logger.trace(f"Main > import resource cost {time() - last_time:.6f}s")

    last_time = time()
    logger.debug("Main > creating main window")
    from src.ui.main_window import MainWindow
    from src.signal import AudioClientSignals, MouseSignals, KeyBoardSignals, JoystickSignals
    main_signals = AudioClientSignals()
    main_window = MainWindow(main_signals, MouseSignals(),
                             KeyBoardSignals(), JoystickSignals())
    logger.trace(f"Main > create main window cost {time() - last_time:.6f}s")

    logger.debug(f"Main > startup completed in {time() - start_time:.6f}s")

    main_window.show()
    exit_code = app.exec()
    resource_rc.qCleanupResources()
    main_window.voice_client.shutdown()  # type: ignore
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
