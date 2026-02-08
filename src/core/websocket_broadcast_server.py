#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT
"""
WebSocket 广播服务：供 ADF 等插件连接，接收并广播状态消息（如频率、PTT 等）。
服务在独立线程的 asyncio 循环中运行，broadcast/stop 从主线程通过 run_coroutine_threadsafe 与服务器线程协作。
"""
from asyncio import CancelledError, get_running_loop, new_event_loop, run_coroutine_threadsafe, set_event_loop, Event
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from websockets import ConnectionClosed, Headers, Request, Response, Server, ServerConnection, serve

from src.constants import version
from src.model import WebSocketMessage


class ClientInfo(BaseModel):
    """单个 WebSocket 连接的信息。"""
    client_id: int
    address: str


class WebSocketBroadcastServer:
    """WebSocket 服务端：仅接受 /ws 路径，维护连接集合并向所有客户端广播消息。"""

    def __init__(self, host: str = '0.0.0.0', port: int = 49080):
        self.server: Optional[Server] = None
        self.host = host
        self.port = port
        self.server_running = Event()
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
        """从任意线程（通常 Qt 主线程）安全地向所有已连接客户端广播。"""
        if self.loop is None or self.server is None or not self.server_running.is_set():
            return
        msg = message.model_dump_json()
        logger.trace(f"Broadcast message: {msg}")
        try:
            future = run_coroutine_threadsafe(self._broadcast(msg), self.loop)
            future.result(timeout=5.0)
        except TimeoutError:
            logger.warning("Broadcast timeout")
        except Exception as e:
            logger.error(f"Broadcast error: {e}")

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
            async for _ in websocket:
                logger.trace(f"Received message from {websocket.remote_address}")
        except ConnectionClosed:
            logger.info("Client disconnect")
        except Exception as e:
            logger.error(f"Fail to handle websocket connection: {e}")
        finally:
            self.unregister(websocket)

    @staticmethod
    async def _pre_progress_request(_: ServerConnection, request: Request) -> Optional[Response]:
        """根路径返回版本信息，供健康检查等。"""
        if request.path == "/*":
            return Response(200, "Success", Headers(), version)
        return None

    async def start(self):
        self.loop = get_running_loop()
        self.server_running.set()
        self.server = await serve(
            self.handler,
            self.host,
            self.port,
            process_request=self._pre_progress_request
        )
        logger.info(f"Websocket server listen on ws://{self.host}:{self.port}")
        try:
            await self.server.serve_forever()
        except CancelledError:
            pass  # 正常关闭时 server.close() 会取消 serve_forever，忽略即可

    async def _stop_async(self) -> None:
        """在服务器所在事件循环中关闭服务（仅供 stop() 内部调度）。"""
        if self.server is not None:
            logger.info("Stop websocket server")
            self.server_running.clear()
            self.server.close()
            await self.server.wait_closed()
            self.server = None

    def stop(self) -> None:
        """从任意线程同步关闭 WebSocket 服务；若服务未启动则无操作。"""
        if self.loop is None or self.server is None:
            return
        try:
            run_coroutine_threadsafe(self._stop_async(), self.loop)
        except TimeoutError:
            logger.warning("WebSocket server stop timeout")
        except Exception as e:
            logger.error(f"WebSocket server stop error: {e}")
