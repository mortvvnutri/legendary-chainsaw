from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from routers.auth import decode_token
from db_connect import get_connection

router = APIRouter(prefix="/ws/team", tags=["team-websocket"])

@router.websocket("/status")
async def team_status_ws(websocket: WebSocket, token: str):
    conn = None
    team_id = None

    try:
        await websocket.accept()

        # Проверка токена (асинхронная)
        payload = await decode_token(token)
        if payload.get("role") != "team":
            await websocket.close()
            return

        team_id = payload["team_id"]

        # Устанавливаем статус online
        conn = await get_connection()
        await conn.execute("UPDATE teams SET status = 'online' WHERE team_id = $1", team_id)

        # Поддержка соединения
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        if team_id:
            try:
                if conn is None:
                    conn = await get_connection()
                await conn.execute("UPDATE teams SET status = 'offline' WHERE team_id = $1", team_id)
            except Exception:
                pass  # Можно логировать при необходимости
    finally:
        if conn:
            await conn.close()
