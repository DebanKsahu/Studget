from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str | None = None
    data: Any | None = None

    @classmethod
    def success_response(cls, data: Any = None, message: str = "Success"):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str = "An error occurred", data: Any = None):
        return cls(success=False, message=message, data=data)