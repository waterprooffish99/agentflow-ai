from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        field: str | None = None,
        request_id: str | None = None,
    ):
        self.code = code
        self.request_id = request_id
        detail = {
            "error": {
                "code": code,
                "message": message,
                "field": field,
            }
        }
        super().__init__(status_code=status_code, detail=detail)


class ValidationError(AppException):
    def __init__(self, message: str, field: str | None = None, request_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            field=field,
            request_id=request_id,
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Invalid credentials", request_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
            request_id=request_id,
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Insufficient permissions", request_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message,
            request_id=request_id,
        )


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource", request_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"{resource} not found",
            request_id=request_id,
        )


class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists", request_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=message,
            request_id=request_id,
        )


class RateLimitError(AppException):
    def __init__(self, request_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please try again later.",
            request_id=request_id,
        )