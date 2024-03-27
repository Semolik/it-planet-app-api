from typing import List, Literal, Union
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from utilities.notifications import send_notification
from cruds.institutions_crud import InstitutionsCrud
from cruds.hobbies_crud import HobbiesCrud
from cruds.users_cruds import UsersCrud
from schemas.users import UserLike, UserRead, UserReadInstitution, UserReadShort,  UserUpdate, UserReadWithEmail
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
    if user_data.email != user.email:
        db_user = await users_crud.get_user_by_email(user_data.email)
        if db_user is not None and db_user.id != user.id:
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


@api_router.get("/me", response_model=UserReadInstitution, name="users:current_user")
async def get_user_me(
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    return await UsersCrud(db).get_user_by_id(current_user.id)


@api_router.get("/recommended", response_model=UserReadShort)
async def get_recommended(
    hobbies_ids: List[uuid.UUID] = Query([]),
    institutions_ids: List[uuid.UUID] = Query([]),
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    for hobby_id in hobbies_ids:
        hobby = await HobbiesCrud(db).get_hobby(hobby_id)
        if not hobby:
            raise HTTPException(status_code=404, detail="Хобби не найдено")

    for institution_id in institutions_ids:
        institution = await InstitutionsCrud(db).get_institution(institution_id=institution_id)
        if not institution:
            raise HTTPException(404, "Образовательное учреждение не найдено")
    return await UsersCrud(db).get_recommended_user(user=current_user, hobbies_ids=hobbies_ids, institutions_ids=institutions_ids)


@api_router.get("/recommended/list", response_model=List[UserReadShort])
async def get_recommended_list(
    hobbies_ids: List[uuid.UUID] = Query([]),
    institutions_ids: List[uuid.UUID] = Query([]),
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    for hobby_id in hobbies_ids:
        hobby = await HobbiesCrud(db).get_hobby(hobby_id)
        if not hobby:
            raise HTTPException(status_code=404, detail="Хобби не найдено")

    for institution_id in institutions_ids:
        institution = await InstitutionsCrud(db).get_institution(institution_id=institution_id)
        if not institution:
            raise HTTPException(404, "Образовательное учреждение не найдено")
    return [
        await UsersCrud(db).get_recommended_user(user=current_user, hobbies_ids=hobbies_ids, institutions_ids=institutions_ids) for _ in range(10)
    ]


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


@api_router.post("/{user_id}/like", response_model=UserLike)
async def like_user(
    user_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    users_crud = UsersCrud(db)
    user = await users_crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Нельзя лайкнуть самого себя")
    user_like = await users_crud.set_user_like(user=current_user, liked_user=user, like=True)
    like_info = UserLike.model_validate(user_like, from_attributes=True)
    like_info.is_match = await users_crud.check_match(user=current_user, liked_user=user)
    if like_info.is_match:
        await send_notification(
            user_id=user.id,
            title="Новый лайк",
            text=f"Пользователь {current_user.name} лайкнул вас в ответ",
            db=db
        )
    return like_info


@api_router.post("/{user_id}/dislike", response_model=UserLike)
async def dislike_user(
    user_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    users_crud = UsersCrud(db)
    user = await users_crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Нельзя дизлайкнуть самого себя")
    user_like = await users_crud.set_user_like(user=current_user, liked_user=user, like=False)
    return user_like


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
