import uuid
from cruds.base_crud import BaseCRUD
from models.locations import Institution
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class InstitutionsCrud(BaseCRUD):

    async def create_institution(self, name: str, city_id: uuid.UUID) -> Institution:
        return await self.create(Institution(name=name, city_id=city_id))

    async def get_institution(self, institution_id: uuid.UUID) -> Institution:
        query = await self.db.execute(select(Institution).where(Institution.id == institution_id).options(selectinload(Institution.city)))
        return query.scalars().first()

    async def get_institutions(self, city_id: uuid.UUID, search_query: str = None, page: int = 1) -> list[Institution]:
        def query_func(q):
            q = q.where(Institution.city_id == city_id)
            if search_query:
                q = q.where(Institution.name.ilike(f"%{search_query}%"))
            return q
        return await self.paginate(
            Institution,
            page=page,
            per_page=20,
            query_func=query_func,
            options=[selectinload(Institution.city)]
        )

    async def update_institution(self, institution: Institution, name: str, city_id: uuid.UUID,) -> Institution:
        institution.name = name
        institution.city_id = city_id
        return await self.update(institution)
