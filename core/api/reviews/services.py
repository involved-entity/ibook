from fastapi import HTTPException, status

from core.api.reviews.schemas import ReviewCreateSchema, ReviewSchema, ReviewUpdateSchema
from core.api.services import CRUDService
from core.database.models import Review


class ReviewsCRUDService(CRUDService):
    model = Review
    schema_class = ReviewSchema
    create_schema_class = ReviewCreateSchema
    update_schema_class = ReviewUpdateSchema

    user_field = "user_id"

    admin_or_owner_to_edit = True
    save_user_id_before_create = True
    list_owner_only = True

    create_entity_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Book not found, or your review with this book exists."
    )
