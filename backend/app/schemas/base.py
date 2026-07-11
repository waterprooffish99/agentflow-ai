from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class PaginationMeta(BaseModel):
    next_cursor: str | None = None
    has_more: bool = False
    total: int | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationMeta