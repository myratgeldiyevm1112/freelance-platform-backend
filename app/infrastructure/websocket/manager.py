import uuid
from fastapi import WebSocket
from app.core.logging import logger


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)
        logger.info(f"WS connected: user_id={user_id}, total={self._active_count()}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self._connections:
            self._connections[user_id].discard if False else None
            try:
                self._connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.info(f"WS disconnected: user_id={user_id}, total={self._active_count()}")

    async def send_to_user(self, user_id: str, event: str, data: dict):
        """Отправить событие конкретному юзеру (всем его соединениям)."""
        sockets = self._connections.get(str(user_id), [])
        if not sockets:
            logger.debug(f"WS send skipped: user_id={user_id} not connected")
            return
        payload = {"event": event, "data": data}
        dead = []
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    def is_connected(self, user_id: str) -> bool:
        return str(user_id) in self._connections

    def _active_count(self) -> int:
        return sum(len(v) for v in self._connections.values())


manager = ConnectionManager()