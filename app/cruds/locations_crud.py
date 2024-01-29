import uuid
from cruds.base_crud import BaseCRUD
from models.locations import City, Institute, University
from sqlalchemy.future import select


class LocationsCrud(BaseCRUD):
    async def create_city(self, name: str) -> City:
        return await self.create(City(name=name))

    async def get_cities(self) -> list[City]:
        query = await self.db.execute(select(City))
        return query.scalars().all()

    async def get_city(self, city_id: uuid.UUID) -> City:
        query = await self.db.execute(select(City).where(City.id == city_id))
        return query.scalars().first()
    
    async def update_city(self, city: City, name: str) -> City:
        city.name = name
        return await self.update(city)
