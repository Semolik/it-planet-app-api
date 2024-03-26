from typing import List
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.params import Query
from schemas.users import UserReadShort, UserLikeFull
from users_controller import current_superuser, current_active_user
from db.db import get_async_session
from cruds.users_cruds import UsersCrud

api_router = APIRouter(prefix="/likes", tags=["likes"])


@api_router.get("/matches", response_model=List[UserLikeFull])
async def get_matches(page: int = Query(1, ge=1), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Возвращает список пользователей, которые взаимно лайкнули текущего пользователя.'''
    return await UsersCrud(db).get_matches(user=current_user, page=page)


@api_router.get("", response_model=List[UserLikeFull])
async def get_likes(page: int = Query(1, ge=1), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Возвращает список пользователей, которых вы лайкнули.'''
    return await UsersCrud(db).get_user_likes(user=current_user, page=page)
