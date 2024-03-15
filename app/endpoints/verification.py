from typing import List
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.params import Query
from fastapi_mail import FastMail, MessageSchema, MessageType
from utilities.notifications import send_notification
from notifier import Notifier, get_notifier
from cruds.verification_crud import VerificationCrud
from cruds.institutions_crud import InstitutionsCrud
from schemas.verification import CreateVerificationRequest, VerificationRequest
from users_controller import current_superuser, current_active_user
from db.db import get_async_session
from mail.conf import conf

api_router = APIRouter(prefix="/verification", tags=["verification"])


@api_router.get("", response_model=List[VerificationRequest], dependencies=[Depends(current_superuser)])
async def get_verification_requests(page: int = Query(1, ge=1), db=Depends(get_async_session)):
    return await VerificationCrud(db).get_verification_requests(page=page)


@api_router.get("/me", response_model=VerificationRequest)
async def get_user_verification_request(
        db=Depends(get_async_session),
        current_user=Depends(current_active_user)):
    verification_request = await VerificationCrud(db).last_active_verification_request(user=current_user)
    if not verification_request:
        raise HTTPException(404, "Запрос на верификацию не найден")
    return verification_request


@api_router.get("/{verification_request_id}", response_model=VerificationRequest, dependencies=[Depends(current_superuser)])
async def get_verification_request(verification_request_id: uuid.UUID, db=Depends(get_async_session)):
    verification_request = await VerificationCrud(db).get_verification_request(verification_request_id=verification_request_id)
    if not verification_request:
        raise HTTPException(404, "Запрос на верификацию не найден")
    return verification_request


@api_router.post("", response_model=VerificationRequest)
async def create_verification_request(
    request: CreateVerificationRequest = Depends(),
    real_photo:  UploadFile = File(
        default=..., description='Реальное фото пользователя'),
    id_photo:  UploadFile = File(
        default=..., description='Фото документа пользователя'),
    db=Depends(get_async_session),
    current_user=Depends(current_active_user), notifier: Notifier = Depends(get_notifier('chats'))
):
    has_active_request = await VerificationCrud(db).last_active_verification_request(user=current_user)
    if has_active_request:
        raise HTTPException(400, "Вы уже отправили запрос на верификацию")
    institution = await InstitutionsCrud(db).get_institution(institution_id=request.institution_id)
    if not institution:
        raise HTTPException(404, "Институт не найден")
    created_request = await VerificationCrud(db).create_verification_request(
        institution_id=request.institution_id,
        real_photo=real_photo,
        id_photo=id_photo,
        user=current_user,
        name=request.name,
        birthdate=request.birthdate
    )
    return await VerificationCrud(db).get_verification_request(verification_request_id=created_request.id)


@api_router.delete("/{verification_request_id}", status_code=204)
async def delete_verification_request(verification_request_id: uuid.UUID, db=Depends(get_async_session),
                                      current_user=Depends(current_active_user)):
    verification_request = await VerificationCrud(db).get_verification_request(verification_request_id=verification_request_id)
    if not verification_request:
        raise HTTPException(404, "Запрос на верификацию не найден")
    if verification_request.user_id != current_user.id:
        raise HTTPException(403, "Нет доступа")
    await VerificationCrud(db).delete(verification_request)


@api_router.put("/{verification_request_id}", response_model=VerificationRequest, dependencies=[Depends(current_superuser)])
async def update_verification_request(verification_request_id: uuid.UUID, approved: bool, db=Depends(get_async_session)):
    verification_request = await VerificationCrud(db).get_verification_request(verification_request_id=verification_request_id)
    if not verification_request:
        raise HTTPException(404, "Запрос на верификацию не найден")
    request = await VerificationCrud(db).update_verification_request(verification_request=verification_request, approved=approved)
    message_title = 'Верификация аккаунта'
    message_text = f"Ваш запрос на верификацию прошел {'успешно' if approved else 'неудачно'}"
    await send_notification(
        user_id=request.user.id,
        header=message_title,
        message=message_text,
        db=db,
    )
    message = MessageSchema(
        subject='Верификация аккаунта',
        recipients=[request.user.email],
        template_body={
                'title': message_title,
                'text': f'''<p>Здравствуйте, {request.user.name}</p><p>{message_text}</p>'''
        },
        subtype=MessageType.html
    )
    try:
        fm = FastMail(conf)
        await fm.send_message(message, template_name='default.html')
    except Exception as e:
        raise HTTPException(500, "Ошибка отправки сообщения")
    return request
