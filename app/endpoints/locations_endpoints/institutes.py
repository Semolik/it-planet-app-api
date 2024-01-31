from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from cruds.institutes_crud import InstitutesCrud
from cruds.cities_crud import CitiesCrud
from cruds.universities_crud import UniversitiesCrud
from schemas.locations import CreateInstitute, Institute
from users_controller import current_superuser
from db.db import get_async_session
from models.user import User


api_router = APIRouter(prefix="/institutes", tags=["institutes"])


@api_router.post("", response_model=Institute)
async def create_institute(institute: CreateInstitute, db=Depends(get_async_session),
                           current_user: User = Depends(current_superuser)):
    city = await CitiesCrud(db).get_city(city_id=institute.city_id)
    if not city:
        raise HTTPException(404, "City not found")
    if institute.university_id:
        university = await UniversitiesCrud(db).get_university(
            university_id=institute.university_id)
        if not university:
            raise HTTPException(404, "University not found")
    city = await InstitutesCrud(db).create_institute(name=institute.name, city_id=institute.city_id, university_id=institute.university_id)
    return await InstitutesCrud(db).get_intstitute(institute_id=city.id)


@api_router.get("", response_model=List[Institute])
async def get_institutes(city_id: uuid.UUID, page: int = Query(1, ge=1), db=Depends(get_async_session)):
    return await InstitutesCrud(db).get_institutes(city_id=city_id, page=page)


@api_router.get("/search", response_model=List[Institute])
async def search_institutes(query: str = None, page: int = Query(1, ge=1), db=Depends(get_async_session)):
    return await InstitutesCrud(db).search_institutes(query=query, page=page)


@api_router.get("/{institute_id}", response_model=Institute)
async def get_institute(institute_id: uuid.UUID, db=Depends(get_async_session)):
    institute = await InstitutesCrud(db).get_intstitute(institute_id=institute_id)
    if not institute:
        raise HTTPException(404, "Institute not found")
    return institute


@api_router.put("/{institute_id}", response_model=Institute)
async def update_institute(institute_id: uuid.UUID, institute: CreateInstitute, db=Depends(get_async_session),
                           current_user: User = Depends(current_superuser)):
    db_institute = await InstitutesCrud(db).get_intstitute(institute_id=institute_id)
    if not db_institute:
        raise HTTPException(404, "Institute not found")
    city = await CitiesCrud(db).get_city(city_id=institute.city_id)
    if not city:
        raise HTTPException(404, "City not found")
    if institute.university_id:
        university = await UniversitiesCrud(db).get_university(
            university_id=institute.university_id)
        if not university:
            raise HTTPException(404, "University not found")
    return await InstitutesCrud(db).update_institute(institute=db_institute, name=institute.name, city_id=institute.city_id, university_id=institute.university_id)


@api_router.delete("/{institute_id}", status_code=204)
async def delete_institute(institute_id: uuid.UUID, db=Depends(get_async_session),
                           current_user: User = Depends(current_superuser)):
    db_institute = await InstitutesCrud(db).get_intstitute(institute_id=institute_id)
    if not db_institute:
        raise HTTPException(404, "Institute not found")
    await InstitutesCrud(db).delete(db_institute)
