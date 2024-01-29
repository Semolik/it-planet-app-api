from typing import List, Literal, Union
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import TypeAdapter
from cruds.locations_crud import LocationsCrud
from schemas.locations import CreateCity, City
from schemas.files import ImageInfo
from users_controller import current_active_user, current_superuser, optional_current_user
from db.db import get_async_session
from models.user import User


api_router = APIRouter(prefix="/cities", tags=["cities"])


@api_router.post("", response_model=City)
async def create_city(city: CreateCity, db=Depends(get_async_session),
                      current_user: User = Depends(current_superuser)):
    return await LocationsCrud(db).create_city(name=city.name)


@api_router.get("", response_model=List[City])
async def get_cities(db=Depends(get_async_session)):
    return await LocationsCrud(db).get_cities()


@api_router.get("/{city_id}", response_model=City)
async def get_city(city_id: uuid.UUID, db=Depends(get_async_session)):
    city = await LocationsCrud(db).get_city(city_id=city_id)
    if not city:
        raise HTTPException(404, "City not found")
    return city
