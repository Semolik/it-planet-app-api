import uuid
from cruds.base_crud import BaseCRUD
from models.locations import Institute, University
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class UniversitiesCrud(BaseCRUD):

    async def get_universities(self, city_id: uuid.UUID, search_query: str = None, page: int = 1, per_page: int = 10) -> list[University]:
        end = page * per_page
        start = end - per_page
        query = (select(University)
                 .options(
            selectinload(University.institutes).selectinload(
                Institute.city)
        )
            .join(Institute, Institute.university_id == University.id)
            .where(Institute.city_id == city_id)
        )
        if search_query:
            query = query.where(University.name.ilike(f"%{search_query}%"))
        query = await self.db.execute(
            query.slice(start, end)
        )
        return query.scalars().all()

    async def get_university(self, university_id: uuid.UUID) -> University:
        query = await self.db.execute(select(University).where(University.id == university_id).options(selectinload(University.institutes).selectinload(Institute.city)))
        return query.scalars().first()

    async def create_university(self, name: str, short_name: str) -> University:
        return await self.create(University(name=name, short_name=short_name))

    async def update_university(self, university: University, name: str, short_name: str) -> University:
        university.name = name
        university.short_name = short_name
        return await self.update(university)

    async def search_universities(self, query: str, page: int = 1, per_page: int = 10) -> list[University]:
        return await self.paginate(
            University,
            page=page,
            per_page=per_page,
            query_func=lambda q: q.where(
                University.name.ilike(f"%{query}%")) if query else q,
            options=[selectinload(University.institutes).selectinload(
                Institute.city)
            ]
        )
