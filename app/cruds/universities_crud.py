import uuid
from cruds.base_crud import BaseCRUD
from models.locations import Institute, University
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class UniversitiesCrud(BaseCRUD):

    async def get_universities(self, city_id: uuid.UUID, page: int = 1, per_page: int = 10) -> list[University]:
        end = page * per_page
        start = end - per_page
        query = await self.db.execute(
            select(University)
            .options(
                selectinload(University.institutes).selectinload(
                    Institute.city)
            )
            .join(Institute, Institute.university_id == University.id)
            .where(Institute.city_id == city_id)
            .slice(start, end)
        )
        return query.scalars().all()

    async def get_university(self, university_id: uuid.UUID) -> University:
        query = await self.db.execute(select(University).where(University.id == university_id).options(selectinload(University.institutes).selectinload(Institute.city)))
        return query.scalars().first()

    async def create_university(self, name: str, short_name: str) -> University:
        return await self.create(University(name=name, short_name=short_name))
