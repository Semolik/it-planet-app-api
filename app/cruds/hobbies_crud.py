import uuid
from cruds.base_crud import BaseCRUD
from models.hobbies import Hobby, UserHobby
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import count


class HobbiesCrud(BaseCRUD):
    async def create_hobby(self, name: str) -> Hobby:
        return await self.create(Hobby(name=name))

    async def get_hobbies(self, page: int, hobby_query: str = None ,page_size: int = 10) -> list[Hobby]:
        end = page * page_size
        start = end - page_size
        query = (select(Hobby).join(UserHobby, Hobby.id == UserHobby.hobby_id, isouter=True).order_by(
            count(UserHobby.user_id).desc()
        ).group_by(Hobby.id, Hobby.name))
        if hobby_query is not None:
            query = query.filter(Hobby.name.ilike(f"%{hobby_query}%"))
        query = await self.db.execute(query.slice(start, end))
        return query.scalars().all()

    async def get_hobby(self, hobby_id: uuid.UUID) -> Hobby:
        query = await self.db.execute(select(Hobby).where(Hobby.id == hobby_id))
        return query.scalars().first()

    async def update_hobby(self, hobby: Hobby, name: str) -> Hobby:
        hobby.name = name
        return await self.update(hobby)
