from typing import List, Literal, Union
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import TypeAdapter
from cruds.users_cruds import UsersCrud
from schemas.users import UserRead, UserUpdate, UserReadWithEmail
from schemas.files import ImageInfo
from users_controller import current_active_user, current_superuser
from db.db import get_async_session
from models.user import User


api_router = APIRouter(prefix="/users", tags=["users"])


async def update_handler(db, user: User, user_data: UserUpdate, current_user: User):
    users_crud = UsersCrud(db)
    if not current_user.is_superuser and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    if current_user.is_superuser:
        # попытка суперадмином понизить себя до обычного пользователя
        if user.id == current_user.id and not user_data.is_superuser:
            raise HTTPException(
                status_code=403, detail="Нельзя понизить себя до обычного пользователя")
    if user_data.email != user.email and await users_crud.get_user_by_email(user_data.email) is not None:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует")
    await users_crud.update_user(user=user, user_data=user_data, update_as_superuser=current_user.is_superuser)
    return await users_crud.get_user_by_id(user.id)


@api_router.put("/me", response_model=UserRead)
async def update_user_me(
    user: UserUpdate,
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    return await update_handler(db=db, user=current_user, user_data=user, current_user=current_user)


@api_router.put("/me/image", response_model=ImageInfo)
async def update_user_me_image(
    userPicture: UploadFile = File(
        default=..., description='Фото пользователя'),
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    users_crud = UsersCrud(db)
    image = await users_crud.update_user_image(user=current_user, image=userPicture)
    return image


@api_router.delete("/me/image", status_code=204)
async def delete_user_me_image(
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    await UsersCrud(db).delete_user_image(user=current_user)


@api_router.put("/{user_id}", response_model=UserReadWithEmail)
async def update_user(
    user: UserUpdate,
    user_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_superuser)
):
    users_crud = UsersCrud(db)
    db_user = await users_crud.get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return await update_handler(db=db, user=db_user, user_data=user, current_user=current_user)


@api_router.get("/me", response_model=UserReadWithEmail, name="users:current_user")
async def get_user_me(
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    return await UsersCrud(db).get_user_by_id(current_user.id)


@api_router.get("/{user_id}", response_model=Union[UserReadWithEmail, UserRead])
async def get_user(
    user_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    user = await UsersCrud(db).get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if current_user.is_superuser:
        return UserReadWithEmail.model_validate(user)
    return UserRead.model_validate(user)


@api_router.get("", response_model=List[UserReadWithEmail])
async def get_users(
    search: str = None,
    page: int = Query(1, ge=1),
    order_by: Literal["name", "register_date"] = "name",
    order: Literal["asc", "desc"] = "asc",
    superusers_to_top: bool = False,
    only_superusers: bool = False,
    is_verified: bool = None,
    db=Depends(get_async_session),
    current_user: User = Depends(current_superuser)
):
    users = await UsersCrud(db).get_users(
        order_by=order_by,
        order=order,
        search=search,
        page=page,
        superusers_to_top=superusers_to_top,
        is_verified=is_verified,
        only_superusers=only_superusers
    )
    return users


@api_router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_superuser)
):
    users_crud = UsersCrud(db)
    user = await users_crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await users_crud.delete(user)
