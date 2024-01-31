import uuid
from cruds.base_crud import BaseCRUD
from models.locations import Institute
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class InstitutesCrud(BaseCRUD):

    async def search_institutes(self, query: str, page: int = 1) -> list[Institute]:
        return await self.paginate(
            Institute,
            page=page,
            per_page=20,
            query_func=lambda q: q.where(
                Institute.name.ilike(f"%{query}%")) if query else q,
            options=[selectinload(Institute.university),
                     selectinload(Institute.city)]
        )

    async def create_institute(self, name: str, city_id: uuid.UUID, university_id: uuid.UUID | None = None) -> Institute:
        return await self.create(Institute(name=name, city_id=city_id, university_id=university_id))

    async def get_intstitute(self, institute_id: uuid.UUID) -> Institute:
        query = await self.db.execute(select(Institute).where(Institute.id == institute_id).options(selectinload(Institute.university), selectinload(Institute.city)))
        return query.scalars().first()

    async def get_institutes(self, city_id: uuid.UUID, page: int = 1) -> list[Institute]:
        return await self.paginate(
            Institute,
            page=page,
            per_page=20,
            query_func=lambda q: q.where(Institute.city_id == city_id),
            options=[selectinload(Institute.university),
                     selectinload(Institute.city)]
        )

    async def update_institute(self, institute: Institute, name: str, city_id: uuid.UUID, university_id: uuid.UUID | None = None) -> Institute:
        institute.name = name
        institute.city_id = city_id
        institute.university_id = university_id
        return await self.update(institute)
