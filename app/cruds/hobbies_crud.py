import uuid

from sqlalchemy import desc,  join
from models.user import User
from cruds.base_crud import BaseCRUD
from models.hobbies import Hobby, UserHobby
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import count
from schemas.hobbies import HobbyWithLike as HobbyWithLikeSchema


class HobbiesCrud(BaseCRUD):
    async def get_hobbies(self, page: int, hobby_query: str = None, current_user: User = None, page_size: int = 30, used: bool = False) -> list[HobbyWithLikeSchema]:
        end = page * page_size
        start = end - page_size

        async def get_hobbies_(liked):
            liked_ = liked and current_user
            query = select(Hobby).join(
                UserHobby, Hobby.id == UserHobby.hobby_id, isouter=not used).order_by(
                desc(count(UserHobby.user_id))).group_by(Hobby.id)
            query = query.slice(start, end)
            if hobby_query:
                query = query.where(Hobby.name.ilike(f"%{hobby_query}%"))
            if liked_:
                query = query.where(UserHobby.user_id == current_user.id)
            elif  used:
                query = query.where(UserHobby.user_id != current_user.id)
            query = query.slice(start, end)
            return (await self.db.execute(query)).scalars().all()
        liked_hobbies = await get_hobbies_(True)
        hobbies = []
        for hobby in liked_hobbies:
            hobby_obj = HobbyWithLikeSchema.model_validate(hobby)
            hobby_obj.liked = True
            hobbies.append(hobby_obj)
        if len(liked_hobbies) > page_size:
            return hobbies
        liked_hobbies_ids = [hobby.id for hobby in liked_hobbies]
        other_hobbies = await get_hobbies_(False)
        for hobby in other_hobbies:
            if hobby.id in liked_hobbies_ids:
                continue
            hobby_obj = HobbyWithLikeSchema.model_validate(hobby)
            hobby_obj.liked = False
            hobbies.append(hobby_obj)
        return hobbies

    async def get_hobby(self, hobby_id: uuid.UUID) -> Hobby:
        query = await self.db.execute(select(Hobby).where(Hobby.id == hobby_id))
        return query.scalars().first()

    async def get_hobby_with_like(self, hobby_id: uuid.UUID, user: User) -> HobbyWithLikeSchema:
        is_liked_subquery = select(UserHobby).where(
            UserHobby.user_id == user.id if user else None).where(UserHobby.hobby_id == Hobby.id).exists()
        query = select(Hobby, is_liked_subquery.label(
            'liked')).where(Hobby.id == hobby_id)
        result = (await self.db.execute(query)).first()
        if not result:
            return None
        obj = HobbyWithLikeSchema.model_validate(result[0])
        obj.liked = result[1]
        return obj

    async def create_hobby(self, name: str) -> Hobby:
        return await self.create(Hobby(name=name))

    async def update_hobby(self, hobby: Hobby, name: str) -> Hobby:
        hobby.name = name
        return await self.update(hobby)

    async def get_user_hobbies(self, user_id: uuid.UUID) -> list[Hobby]:
        query = await self.db.execute(select(Hobby).join(UserHobby).where(UserHobby.user_id == user_id))
        return query.scalars().all()

    async def get_user_hobbies_with_like(self, user_id: uuid.UUID) -> list[HobbyWithLikeSchema]:
        hobbies = await self.get_user_hobbies(user_id)
        hobbies_with_like = []
        for hobby in hobbies:
            hobby_obj = HobbyWithLikeSchema.model_validate(hobby)
            hobby_obj.liked = True
            hobbies_with_like.append(hobby_obj)
        return hobbies_with_like

    async def add_user_hobby(self, user: User, hobby: Hobby) -> UserHobby:
        return await self.create(UserHobby(user_id=user.id, hobby_id=hobby.id))

    async def get_user_hobby(self, user: User, hobby: Hobby) -> UserHobby:
        query = await self.db.execute(select(UserHobby).where(UserHobby.user_id == user.id).where(UserHobby.hobby_id == hobby.id))
        return query.scalars().first()
