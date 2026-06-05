from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.security import decode_token
from app.infrastructure.websocket.manager import manager
from app.core.logging import logger

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    user_id: str,
    websocket: WebSocket,
    token: str = Query(...),
):
    try:
        payload = decode_token(token)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"WS rejected: invalid token for user_id={user_id}")
        return

    if payload.get("type") != "access":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if str(payload.get("sub")) != str(user_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("WS rejected: token sub != path user_id")
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)