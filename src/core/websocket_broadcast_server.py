#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from asyncio import get_running_loop, new_event_loop, set_event_loop
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from websockets import ConnectionClosed, Headers, Request, Response, Server, ServerConnection, serve

from src.constants import version
from src.model import WebSocketMessage


class ClientInfo(BaseModel):
    client_id: int
    address: str


# ADF插件
class WebSocketBroadcastServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 49080):
        self.server: Optional[Server] = None
        self.host = host
        self.port = port
        self.clients: set[ServerConnection] = set()
        self.client_info: dict[ServerConnection, ClientInfo] = {}
        try:
            self.loop = get_running_loop()
        except RuntimeError:
            self.loop = new_event_loop()
            set_event_loop(self.loop)

    async def register(self, websocket: ServerConnection) -> None:
        self.clients.add(websocket)
        client_id = id(websocket)
        address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.client_info[websocket] = ClientInfo(client_id=client_id, address=address)
        logger.info(f"New connection from {address}, ID: {client_id}")
        logger.info(f"Current connection: {len(self.clients)}")

    def unregister(self, websocket: ServerConnection) -> None:
        if websocket in self.clients:
            client_id = self.client_info[websocket].client_id
            self.clients.remove(websocket)
            del self.client_info[websocket]
            logger.info(f"Client disconnect: {client_id}")
            logger.info(f"Current connection: {len(self.clients)}")

    def broadcast(self, message: WebSocketMessage):
        msg = message.model_dump_json()
        logger.trace(f"Broadcast message: {msg}")
        self.loop.run_until_complete(self._broadcast(msg))

    async def _broadcast(self, message: str):
        if not self.clients:
            return

        disconnected_clients = set()

        for client in self.clients:
            try:
                await client.send(message)
            except Exception as e:
                logger.error(f"Fail broadcast message: {e}")
                disconnected_clients.add(client)

        for client in disconnected_clients:
            self.unregister(client)

    async def handler(self, websocket: ServerConnection) -> None:
        if websocket.request is None:
            await websocket.close(1002, "please use websocket")
            return
        if websocket.request.path != "/ws":
            await websocket.close(1002, "please use websocket")
            return
        await self.register(websocket)
        try:
            async for message in websocket:
                logger.trace(f"Received message from {websocket.remote_address}: {message}")
        except ConnectionClosed:
            logger.info("Client disconnect")
        except Exception as e:
            logger.error(f"Fail to handle websocket connection: {e}")
        finally:
            self.unregister(websocket)

    @staticmethod
    async def _pre_progress_request(_: ServerConnection, request: Request) -> Optional[Response]:
        if request.path == "/*":
            return Response(200, "Success", Headers(), version)
        return None

    async def start(self):
        self.server = await serve(
            self.handler,
            self.host,
            self.port,
            process_request=self._pre_progress_request
        )
        logger.info(f"Websocket server listen on ws://{self.host}:{self.port}")
        await self.server.serve_forever()

    async def stop(self):
        if hasattr(self, 'server') and self.server is not None:
            logger.info(f"Stop websocket server")
            self.server.close()
            await self.server.wait_closed()
