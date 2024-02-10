import uuid

from fastapi import UploadFile
from schemas.users import ChageOnApproveUserData
from models.user import User
from cruds.base_crud import BaseCRUD
from models.verification import VerificationRequest
from models.locations import Institution
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from utilities.files import duplicate_image, save_image


class VerificationCrud(BaseCRUD):
    async def get_verification_requests(self, page: int = 1) -> list[VerificationRequest]:
        return await self.paginate(VerificationRequest, page=page, query_func=lambda q: q.order_by(VerificationRequest.creation_date.desc()))

    def add_options_to_query(self, query):
        return query.options(
            selectinload(VerificationRequest.real_photo),
            selectinload(VerificationRequest.id_photo),
            selectinload(VerificationRequest.institution).selectinload(
                Institution.city),
            selectinload(VerificationRequest.user)
        )

    async def get_verification_request(self, verification_request_id: uuid.UUID) -> VerificationRequest:
        query = await self.db.execute(self.add_options_to_query(select(VerificationRequest)
                                      .where(VerificationRequest.id == verification_request_id)
        ))
        return query.scalars().first()

    async def last_active_verification_request(self, user: User) -> bool:
        query = await self.db.execute(self.add_options_to_query(select(VerificationRequest)
                                      .order_by(VerificationRequest.creation_date.desc())
                                      .where(VerificationRequest.user_id == user.id)
                                      .where(VerificationRequest.reviewed == False)))
        return query.scalars().first()

    async def create_verification_request(self, institution_id: uuid.UUID, real_photo: UploadFile, id_photo: UploadFile, user: User, user_data: ChageOnApproveUserData) -> VerificationRequest:
        real_photo_model = await save_image(db=self.db, upload_file=real_photo)
        id_photo_model = await save_image(db=self.db, upload_file=id_photo)
        return await self.create(
            VerificationRequest(
                user_id=user.id,
                institution_id=institution_id,
                real_photo_id=real_photo_model.id,
                id_photo_id=id_photo_model.id,
                name=user_data.name,
                birthdate=user_data.birthdate
            )
        )

    async def update_verification_request(self, verification_request: VerificationRequest, approved: bool) -> VerificationRequest:
        verification_request.reviewed = True
        user: User = verification_request.user
        user.verified = approved
        if approved:
            user.name = verification_request.name
            user.birthdate = verification_request.birthdate
            new_profile_image = duplicate_image(
                db=self.db, image=verification_request.real_photo)
            if user.image_id:
                await self.delete(user.image)
            user.image_id = new_profile_image.id
        await self.update(user)
        return await self.update(verification_request)
