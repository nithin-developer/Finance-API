from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _serialize_validation_errors(exc: RequestValidationError) -> list[dict]:
    # pydantic v2 can include raw input values (including bytes),
    # which are not always JSON-serializable in response bodies.
    try:
        return exc.errors(include_input=False)
    except TypeError:
        # Compatibility fallback if include_input is unavailable.
        return jsonable_encoder(exc.errors())


def register_exception_handlers(app) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation failed",
                "errors": _serialize_validation_errors(exc),
                "path": request.url.path,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": detail, "path": request.url.path},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "path": request.url.path,
            },
        )
