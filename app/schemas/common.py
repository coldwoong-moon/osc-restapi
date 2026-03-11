from typing import Generic, TypeVar

from pydantic import BaseModel

from app.core.exceptions import ErrorResponse

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


__all__ = ["PaginatedResponse", "ErrorResponse"]
