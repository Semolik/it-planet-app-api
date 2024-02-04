from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from cruds.cities_crud import CitiesCrud
from schemas.locations import CreateCity, City
from users_controller import current_superuser
from db.db import get_async_session
from models.user import User


api_router = APIRouter(prefix="/cities", tags=["cities"])


@api_router.post("", response_model=City, dependencies=[Depends(current_superuser)])
async def create_city(city: CreateCity, db=Depends(get_async_session)):
    return await CitiesCrud(db).create_city(name=city.name)


@api_router.get("", response_model=List[City])
async def get_cities(db=Depends(get_async_session)):
    return await CitiesCrud(db).get_cities()


@api_router.get("/{city_id}", response_model=City)
async def get_city(city_id: uuid.UUID, db=Depends(get_async_session)):
    city = await CitiesCrud(db).get_city(city_id=city_id)
    if not city:
        raise HTTPException(404, "City not found")
    return city


@api_router.put("/{city_id}", response_model=City, dependencies=[Depends(current_superuser)])
async def update_city(city_id: uuid.UUID, city: CreateCity, db=Depends(get_async_session)):
    db_city = await CitiesCrud(db).get_city(city_id=city_id)
    if not db_city:
        raise HTTPException(404, "City not found")
    return await CitiesCrud(db).update_city(city=db_city, name=city.name)


@api_router.delete("/{city_id}", status_code=204, dependencies=[Depends(current_superuser)])
async def delete_city(city_id: uuid.UUID, db=Depends(get_async_session)):
    db_city = await CitiesCrud(db).get_city(city_id=city_id)
    if not db_city:
        raise HTTPException(404, "City not found")
    if await CitiesCrud(db).city_has_institutes(city_id=city_id):
        raise HTTPException(400, "City has institutes")
    await CitiesCrud(db).delete(db_city)
