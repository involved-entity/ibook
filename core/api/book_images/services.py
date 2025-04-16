import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.book_images.schemas import BookImageCreateSchema, BookImageSchema, BookImageUpdateSchema
from core.api.services import C, CRUDService, M
from core.config import settings
from core.database.models import Book, BookImage, User
from core.database.models.user import UserRole

UPLOAD_DIR = Path(settings.upload_book_images_dir)


async def _save_uploaded_file(file: UploadFile) -> str:  # noqa
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / filename
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(1024):
            await f.write(chunk)

    return str(filename)


async def save_uploaded_book_image(file: UploadFile, book_id: int, is_main: bool) -> BookImage:
    filename = await _save_uploaded_file(file)

    return BookImage(
        book_id=book_id,
        url=filename,
        is_main=is_main,
    )


class BookImagesCRUDService(CRUDService):
    model = BookImage
    schema_class = BookImageSchema
    create_schema_class = BookImageCreateSchema
    update_schema_class = BookImageUpdateSchema

    async def _check_perms_to_book(self, book_id: int, user: User, session: AsyncSession) -> Book:
        book = await session.get(Book, book_id)

        if not book:
            raise self.create_entity_error

        if user.role != UserRole.ADMIN and user.id != book.seller_id:
            raise self.permission_denied_error

        return book  # noqa

    async def check_permissions_to_edit_entity(self, entity: M, user: User, session: AsyncSession) -> M:
        await self._check_perms_to_book(entity.book_id, user, session)

        return entity

    async def before_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:
        await self._check_perms_to_book(create_entity.book_id, user, session)

        filename = await _save_uploaded_file(create_entity.file)
        entity.url = filename

        return entity
