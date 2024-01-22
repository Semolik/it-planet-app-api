import uuid
from sqlalchemy.orm import selectinload
from sqlalchemy import select, or_, nulls_first

from cruds.base_crud import BaseCRUD
from models.user import User
from schemas.users import UserUpdate
from users_controller import get_user_manager_context


class UsersCrud(BaseCRUD):
    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        query = await self.db.execute(select(User).where(User.id == user_id).options(selectinload(User.faculty)))
        return query.scalars().first()

    async def get_user_by_email(self, email: str) -> User:
        user = select(User).where(User.email == email)
        result = await self.db.execute(user)
        return result.scalars().first()

    async def get_users(self, order_by: str = "name", order: str = "asc", search: str = None, page: int = 1, superusers_to_top: bool = False, only_superusers: bool = False, is_verified: bool = None,
                        page_size: int = 20) -> list[User]:
        order_query = getattr(User, order_by).asc(
        ) if order == "asc" else getattr(User, order_by).desc()
        users = select(User)
        if superusers_to_top:
            users = users.order_by(nulls_first(
                User.is_superuser.desc()), order_query)
        else:
            users = users.order_by(order_query)
        if search:
            users = users.where(
                or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")))
        if only_superusers:
            users = users.where(User.is_superuser == True)
        if is_verified is not None:
            users = users.where(User.is_verified == is_verified)
        users = users.offset(
            (page - 1) * page_size).limit(page_size)
        result = await self.db.execute(users)
        return result.scalars().all()

    async def update_user(self, user: User, user_data: UserUpdate, update_as_superuser: bool = False) -> User:
        if update_as_superuser:
            user.is_superuser = user_data.is_superuser
            user.is_active = user_data.is_active
            user.is_verified = user_data.is_verified
        user.name = user_data.name
        if user_data.password:
            async with get_user_manager_context(self.db) as user_manager:
                user.hashed_password = user_manager.password_helper.hash(
                    user_data.password)
        if user.email != user_data.email:
            user.email = user_data.email
            user.is_verified = False
            user = await self.update(user)
            async with get_user_manager_context(self.db) as user_manager:
                await user_manager.request_verify(user)
        else:
            user = await self.update(user)
        return user
