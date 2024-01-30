import uuid
from cruds.base_crud import BaseCRUD
from models.locations import City, Institute, University
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class LocationsCrud(BaseCRUD):
    async def create_city(self, name: str) -> City:
        return await self.create(City(name=name))

    async def get_cities(self) -> list[City]:
        query = await self.db.execute(select(City))
        return query.scalars().all()

    async def get_city(self, city_id: uuid.UUID) -> City:
        query = await self.db.execute(select(City).where(City.id == city_id))
        return query.scalars().first()

    async def city_has_institutes(self, city_id: uuid.UUID) -> bool:
        query = await self.db.execute(select(Institute).where(Institute.city_id == city_id))
        return query.scalars().first() is not None

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

    async def update_city(self, city: City, name: str) -> City:
        city.name = name
        return await self.update(city)

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

    async def get_university(self, university_id: uuid.UUID) -> University:
        query = await self.db.execute(select(University).where(University.id == university_id).options(selectinload(University.institutes).selectinload(Institute.city)))
        return query.scalars().first()

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

    async def create_university(self, name: str, short_name: str) -> University:
        return await self.create(University(name=name, short_name=short_name))
