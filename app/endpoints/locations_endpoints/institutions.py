from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from cruds.institutions_crud import InstitutionsCrud
from cruds.cities_crud import CitiesCrud
from schemas.locations import CreateInstitution, Institution
from users_controller import current_superuser
from db.db import get_async_session
from models.user import User


api_router = APIRouter(prefix="/institutions", tags=["institutions"])


@api_router.post("", response_model=Institution)
async def create_institution(institution: CreateInstitution, db=Depends(get_async_session),
                             current_user: User = Depends(current_superuser)):
    city = await CitiesCrud(db).get_city(city_id=institution.city_id)
    if not city:
        raise HTTPException(404, "Город не найден")
    institution = await InstitutionsCrud(db).create_institution(name=institution.name, city_id=institution.city_id)
    return await InstitutionsCrud(db).get_institution(institution_id=institution.id)


@api_router.get("", response_model=List[Institution])
async def get_institutions(city_id: uuid.UUID, query: str = None, page: int = Query(1, ge=1), db=Depends(get_async_session)):
    return await InstitutionsCrud(db).get_institutions(city_id=city_id, page=page, search_query=query)


@api_router.get("/{institution_id}", response_model=Institution)
async def get_institution(institution_id: uuid.UUID, db=Depends(get_async_session)):
    institution = await InstitutionsCrud(db).get_institution(institution_id=institution_id)
    if not institution:
        raise HTTPException(404, "Образовательное учреждение не найдено")
    return institution


@api_router.put("/{institution_id}", response_model=Institution)
async def update_institution(institution_id: uuid.UUID, institution: CreateInstitution, db=Depends(get_async_session),
                             current_user: User = Depends(current_superuser)):
    db_institution = await InstitutionsCrud(db).get_institution(institution_id=institution_id)
    if not db_institution:
        raise HTTPException(404, "Образовательное учреждение не найдено")
    city = await CitiesCrud(db).get_city(city_id=institution.city_id)
    if not city:
        raise HTTPException(404, "Город не найден")
    return await InstitutionsCrud(db).update_institution(institution=db_institution, name=institution.name, city_id=institution.city_id)


@api_router.delete("/{institution_id}", status_code=204)
async def delete_institution(institution_id: uuid.UUID, db=Depends(get_async_session),
                             current_user: User = Depends(current_superuser)):
    db_institution = await InstitutionsCrud(db).get_institution(institution_id=institution_id)
    if not db_institution:
        raise HTTPException(404, "Образовательное учреждение не найдено")
    await InstitutionsCrud(db).delete(db_institution)
