from __future__ import annotations

import typing

from pydantic import BaseModel

S = typing.TypeVar("S", bound=BaseModel)


class ListPaginatedResponse(BaseModel, typing.Generic[S]):
    items: list[S]
    total: int
    pages: int | None = None

    class Config:
        arbitrary_types_allowed = True
