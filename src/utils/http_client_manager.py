#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from threading import Thread
from time import time
from typing import Optional

from PySide6.QtCore import QObject, Signal
from httpx import Client, Request, Response
from loguru import logger


class HttpClientManger(QObject):
    client_initialized: Signal = Signal()

    def __init__(self, /):
        super().__init__()
        self._http_client: Optional[Client] = None

    def initialize(self):
        Thread(target=self._initialize, daemon=True).start()

    @staticmethod
    def _log_request(request: Request):
        logger.trace(f"HttpClientManger > send http request: {request.method} {request.url} - Waiting for response")

    @staticmethod
    def _log_response(response: Response):
        request = response.request
        logger.trace(f"HttpClientManger > received http response: {request.method} {request.url} - Status {response.status_code}")

    def _initialize(self):
        start_time = time()
        logger.trace("HttpClientManger > initializing http client")

        self._http_client = Client(event_hooks={
            "request": [HttpClientManger._log_request],
            "response": [HttpClientManger._log_response]
        })

        logger.trace(f"HttpClientManger > initialize http client cost {time() - start_time:.6f}s")

        self.client_initialized.emit()

    @property
    def client(self) -> Client:
        assert self._http_client is not None, "Http client not initialized"
        return self._http_client


http_client_manager = HttpClientManger()
