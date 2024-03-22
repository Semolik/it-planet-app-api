import uuid
from cruds.base_crud import BaseCRUD
from models.locations import City, Institution
from sqlalchemy.future import select


class CitiesCrud(BaseCRUD):
    async def create_city(self, name: str) -> City:
        return await self.create(City(name=name))

    async def get_cities(self, query: str = None, page: int = 1):
        def query_func(q):
            if query:
                q = q.where(City.name.ilike(f"%{query}%"))
            return q
        return await self.paginate(
            City,
            page=page,
            per_page=30,
            query_func=query_func
        )

    async def get_city(self, city_id: uuid.UUID) -> City:
        query = await self.db.execute(select(City).where(City.id == city_id))
        return query.scalars().first()

    async def city_has_institutions(self, city_id: uuid.UUID) -> bool:
        query = await self.db.execute(select(Institution).where(Institution.city_id == city_id))
        return query.scalars().first() is not None

    async def update_city(self, city: City, name: str) -> City:
        city.name = name
        return await self.update(city)
