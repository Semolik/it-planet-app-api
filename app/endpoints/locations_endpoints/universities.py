from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from cruds.universities_crud import UniversitiesCrud
from schemas.locations import CreateUniversity, University
from users_controller import current_superuser
from db.db import get_async_session
from models.user import User


api_router = APIRouter(prefix="/universities", tags=["universities"])


@api_router.post("", response_model=University)
async def create_university(university: CreateUniversity, db=Depends(get_async_session),
                            current_user: User = Depends(current_superuser)):
    university = await UniversitiesCrud(db).create_university(name=university.name, short_name=university.short_name)
    return await UniversitiesCrud(db).get_university(university_id=university.id)


@api_router.get("", response_model=List[University])
async def get_universities(city_id: uuid.UUID, query: str = None, page: int = Query(1, ge=1), db=Depends(get_async_session)):
    return await UniversitiesCrud(db).get_universities(city_id=city_id, page=page, search_query=query)


@api_router.get("/{university_id}", response_model=University)
async def get_university(university_id: uuid.UUID, db=Depends(get_async_session)):
    university = await UniversitiesCrud(db).get_university(university_id=university_id)
    if not university:
        raise HTTPException(404, "University not found")
    return university


@api_router.put("/{university_id}", response_model=University)
async def update_university(university_id: uuid.UUID, university: CreateUniversity, db=Depends(get_async_session),
                            current_user: User = Depends(current_superuser)):
    db_university = await UniversitiesCrud(db).get_university(university_id=university_id)
    if not db_university:
        raise HTTPException(404, "University not found")
    return await UniversitiesCrud(db).update_university(university=db_university, name=university.name, short_name=university.short_name)


@api_router.delete("/{university_id}", status_code=204)
async def delete_university(university_id: uuid.UUID, db=Depends(get_async_session),
                            current_user: User = Depends(current_superuser)):
    db_university = await UniversitiesCrud(db).get_university(university_id=university_id)
    if not db_university:
        raise HTTPException(404, "University not found")
    await UniversitiesCrud(db).delete(db_university)
