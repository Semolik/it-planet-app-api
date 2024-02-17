from fastapi import Depends, WebSocket, WebSocketException
from db.db import get_async_session
from users_controller import verify_token


async def get_user_from_cookie(websocket: WebSocket, db=Depends(get_async_session)):
    cookie = websocket.cookies.get("fastapiusersauth")
    user = await verify_token(token=cookie, db=db)
    if not user or not user.is_active:
        raise WebSocketException(code=401, reason="Unauthorized")
    return user
