from typing import List
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.params import Query
from cruds.hobbies_crud import HobbiesCrud
from users_controller import current_superuser, current_active_user
from schemas.hobbies import Hobby
from db.db import get_async_session
from mail.conf import conf

api_router = APIRouter(prefix="/hobbies", tags=["hobbies"])


@api_router.post("", response_model=Hobby, dependencies=[Depends(current_superuser)])
async def create_hobby(name: str, db=Depends(get_async_session)):
    return await HobbiesCrud(db).create_hobby(name=name)


@api_router.get("", response_model=List[Hobby])
async def get_hobbies(page: int = Query(ge=1), query: str = None, db=Depends(get_async_session)):
    '''Возвращает список хобби, отсортированный по количеству пользователей, занимающихся этим хобби.'''
    return await HobbiesCrud(db).get_hobbies(page=page,hobby_query = query)


@api_router.put("/{hobby_id}", response_model=Hobby, dependencies=[Depends(current_superuser)])
async def update_hobby(hobby_id: uuid.UUID, name: str, db=Depends(get_async_session)):
    hobby = await HobbiesCrud(db).get_hobby(hobby_id)
    if not hobby:
        raise HTTPException(status_code=404, detail="Хобби не найдено")
    return await HobbiesCrud(db).update_hobby(hobby, name=name)


@api_router.get("/{hobby_id}", response_model=Hobby)
async def get_hobby(hobby_id: uuid.UUID):
    '''Возвращает хобби по его id.'''
    hobby = await HobbiesCrud().get_hobby(hobby_id)
    if not hobby:
        raise HTTPException(status_code=404, detail="Хобби не найдено")
    return hobby


@api_router.delete("/{hobby_id}", dependencies=[Depends(current_superuser)], status_code=204)
async def delete_hobby(hobby_id: uuid.UUID, db=Depends(get_async_session)):
    hobby = await HobbiesCrud(db).get_hobby(hobby_id)
    if not hobby:
        raise HTTPException(status_code=404, detail="Хобби не найдено")
    await HobbiesCrud(db).delete(hobby)
    