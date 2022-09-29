from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException

from app.api.errors.validation_error import validation_error_handler
from app.api.errors.http_error import http_error_handler
from app.api.routes.api import router as api_router


def get_application() -> FastAPI:
    application = FastAPI()

    application.include_router(api_router)

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)

    return application


app = get_application()
