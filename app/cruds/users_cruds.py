import uuid
from fastapi import UploadFile
from sqlalchemy.orm import selectinload
from sqlalchemy import select, or_, nulls_first, and_
from models.files import Image
from cruds.base_crud import BaseCRUD
from utilities.files import save_image
from models.user import User, UserLike
from schemas.users import UserLikeFull, UserUpdate
from users_controller import get_user_manager_context


class UsersCrud(BaseCRUD):
    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        query = await self.db.execute(select(User).where(User.id == user_id).options(selectinload(User.image)))
        return query.scalars().first()

    async def get_user_by_email(self, email: str) -> User:
        user = select(User).where(User.email == email).options(
            selectinload(User.image))
        result = await self.db.execute(user)
        return result.scalars().first()

    async def update_user_image(self, user: User, image: UploadFile) -> Image | None:
        if user.image_id:
            image_id = user.image_id
            user.image_id = None
            old_image = await self.get(image_id, Image)
            await self.delete(old_image)
        image_model = await save_image(db=self.db, upload_file=image)
        user.image_id = image_model.id
        await self.update(user)
        return image_model

    async def delete_user_image(self, user: User) -> None:
        if user.image_id:
            image_id = user.image_id
            user.image_id = None
            old_image = await self.get(image_id, Image)
            await self.delete(old_image)
            await self.update(user)

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

    async def get_user_like(self, user: User, liked_user: User) -> UserLike:
        query = await self.db.execute(select(UserLike).where(UserLike.user_id == user.id).where(UserLike.liked_user_id == liked_user.id))
        return query.scalars().first()

    async def set_user_like(self, user: User, liked_user: User, like: bool) -> UserLike:
        user_like = await self.get_user_like(user, liked_user)
        if user_like:
            user_like.like = like
            return await self.update(user_like)
        return await self.create(UserLike(user_id=user.id, liked_user_id=liked_user.id, like=like))

    async def check_match(self, user: User, liked_user: User) -> bool:
        user_like = await self.get_user_like(user, liked_user)
        if not user_like:
            return False
        liked_user_like = await self.get_user_like(liked_user, user)
        if not liked_user_like:
            return False
        return user_like.like and liked_user_like.like

    async def get_matches(self, user: User, page: int = 1, page_size: int = 20) -> list[User]:
        user_id = user.id
        end = page * page_size
        start = end - page_size
        query = await self.db.execute(
            select(User)
            .join(UserLike, UserLike.liked_user_id == User.id)
            .where(
                UserLike.user_id == user_id,
                UserLike.like == True,
                UserLike.liked_user_id.in_(
                    select(UserLike.user_id).where(
                        UserLike.liked_user_id == user_id,
                        UserLike.like == True
                    )
                )
            )
            .order_by(UserLike.like_date.desc())
            .slice(start, end)
        )

        return query.scalars().all()

    async def get_user_likes(self, user: User, page: int = 1, page_size: int = 20) -> list[UserLikeFull]:
        user_id = user.id
        end = page * page_size
        start = end - page_size
        subquery = select(UserLike.like).where(
            and_(
                UserLike.user_id == UserLike.liked_user_id,
                UserLike.user_id == user_id,
                UserLike.like == True
            )
        ).as_scalar()
        query = await self.db.execute(
            select(User, subquery)
            .join(UserLike, UserLike.liked_user_id == User.id)
            .where(UserLike.user_id == user_id)
            .options(
                selectinload(User.image)
            )
            .order_by(UserLike.like_date.desc())
            .slice(start, end)
        )

        return [UserLikeFull(is_match=is_match is not None, liked_user=user) for user, is_match in query.all()]
