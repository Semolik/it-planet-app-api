import uuid

from cruds.base_crud import BaseCRUD
from models.files import Image


class FilesCRUD(BaseCRUD):
    async def get_image_by_id(self, image_id: uuid.UUID) -> Image:
        return await self.get(image_id, Image)
