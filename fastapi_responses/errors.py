from http import HTTPStatus
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_responses.response import Response


ERROR_MESSAGES: dict[int, str] = {
    401: "Authentication required",
    403: "You don't have permission to perform this action",
    404: "Resource not found",
    400: "Invalid request",
    422: "Invalid request data",
    500: "An unexpected error occurred",
}


class ErrorResponse(Exception):
    """Standard error response that includes error message."""

    def __init__(self, error: str, status_code: int = HTTPStatus.BAD_REQUEST) -> None:
        """Initialize error response with message and status code.

        Args:
            error: Error message to return
            status_code: HTTP status code for the response
        """

        self.error = error
        self.status_code = status_code

        super().__init__(error)

    @classmethod
    def from_status_code(cls, status_code: int) -> "ErrorResponse":
        """Create an error response from a status code.

        Args:
            status_code: HTTP status code to get error message for

        Returns:
            ErrorResponse with the appropriate error message for the status code
        """

        return cls(
            error=ERROR_MESSAGES.get(status_code, ERROR_MESSAGES[500]),
            status_code=status_code,
        )


def setup_error_handlers(app: FastAPI) -> None:
    """Set up global error handlers for the application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors from pydantic models."""

        logging.exception(exc)

        response = Response(success=False, error=ERROR_MESSAGES[422])

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(ErrorResponse)
    async def error_response_handler(_: Request, exc: ErrorResponse) -> JSONResponse:
        """Convert ErrorResponse exceptions to proper JSONResponse objects."""

        logging.info("ErrorResponse: %s - %s", exc.status_code, exc.error)

        response = Response(success=False, error=exc.error)

        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        """Handle all unhandled exceptions."""

        logging.exception(exc)

        response = Response(success=False, error=ERROR_MESSAGES[500])

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.model_dump(mode="json"),
        )
