import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.selectable import Select

from core.api.books.schemas import BookCreateSchema, BookSchema
from core.api.services import C, CRUDService, M
from core.config import settings
from core.database.models import Book, BookCategory, BookImage, Category, User

UPLOAD_DIR = Path(settings.upload_book_images_dir)


class BooksCRUDService(CRUDService):
    model = Book
    schema_class = BookSchema
    create_schema_class = BookCreateSchema

    user_field = "seller_id"

    admin_or_owner_to_edit = True
    save_user_id_before_create = True

    def get_entities_default_query(self) -> Select:
        return (
            select(self.model)
            .options(
                joinedload(self.model.seller),
                selectinload(self.model.order_items),
                selectinload(self.model.images),
                selectinload(self.model.categories).joinedload(BookCategory.category),
            )
            .order_by(self.model.id)
        )

    async def after_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:
        if create_entity.categories:
            stmt = select(Category).where(Category.name.in_(create_entity.categories))
            existing_categories = await session.scalars(stmt)

            for category in existing_categories:
                book_category = BookCategory(book_id=entity.id, category_id=category.id)  # noqa
                session.add(book_category)

            await session.commit()

        if create_entity.images:
            for img_data in create_entity.images:
                filename = await self._save_uploaded_file(img_data.file)

                book_image = BookImage(
                    book_id=entity.id,  # noqa
                    url=filename,
                    is_main=img_data.is_main,
                )
                session.add(book_image)

            await session.commit()

        return entity

    async def _save_uploaded_file(self, file: UploadFile) -> str:  # noqa
        file_ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        file_path = UPLOAD_DIR / filename
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(1024):
                await f.write(chunk)

        return str(filename)
