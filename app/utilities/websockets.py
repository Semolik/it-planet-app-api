from fastapi import Depends, WebSocket, WebSocketException
from users_controller import get_jwt_strategy, get_user_manager


async def get_user_from_cookie(websocket: WebSocket, user_manager=Depends(get_user_manager), is_verified: bool = False):
    cookie = websocket.cookies.get("fastapiusersauth")
    user = await get_jwt_strategy().read_token(cookie, user_manager)
    if not user or not user.is_active or user.is_verified if is_verified else False:
        raise WebSocketException("Invalid user")
    yield user
