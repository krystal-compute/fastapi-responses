from pydantic import BaseModel


class Response[T](BaseModel):
    """Response model."""

    success: bool
    data: T | None = None
    error: str | None = None
