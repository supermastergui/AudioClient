from asyncio import get_running_loop, new_event_loop, set_event_loop
from json import dumps
from typing import Optional, Set

from loguru import logger
from websockets import ConnectionClosed, Headers, Request, Response, ServerConnection, serve

from src.model import WebSocketMessage


# ADF插件
class WebSocketBroadcastServer:
    def __init__(self, host='0.0.0.0', port=49080):
        self.server = None
        self.host = host
        self.port = port
        self.clients: Set[ServerConnection] = set()
        self.client_info = {}

    async def register(self, websocket: ServerConnection) -> None:
        self.clients.add(websocket)
        client_id = id(websocket)
        self.client_info[websocket] = {
            "id": client_id,
            "address": websocket.remote_address
        }
        logger.info(f"New connection from {websocket.remote_address}, ID: {client_id}")
        logger.info(f"Current connection: {len(self.clients)}")

    def unregister(self, websocket: ServerConnection) -> None:
        if websocket in self.clients:
            client_id = self.client_info[websocket]['id']
            self.clients.remove(websocket)
            del self.client_info[websocket]
            logger.info(f"Client disconnect: {client_id}")
            logger.info(f"Current connection: {len(self.clients)}")

    def broadcast(self, message: WebSocketMessage):
        message = dumps(message.to_dict())
        logger.trace(f"Broadcast message: {message}")
        try:
            loop = get_running_loop()
        except RuntimeError:
            loop = new_event_loop()
            set_event_loop(loop)
        loop.run_until_complete(self._broadcast(message))

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
            return Response(200, "Success", Headers(), b"AudioClient/1.0.0")
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
        if hasattr(self, 'server'):
            self.server.close()
            await self.server.wait_closed()
