from fastapi import FastAPI
from fastapi.responses import JSONResponse


class BadRequestError(Exception):
    def __init__(self, message: str):
        self.message = message


class ServerError(Exception):
    def __init__(self, message: str):
        self.message = message


def init_exception_handlers(app: FastAPI):
    @app.exception_handler(BadRequestError)
    async def bad_request_handler(_, exc: BadRequestError):
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(ServerError)
    async def server_error_handler(_, exc: ServerError):
        return JSONResponse(status_code=500, content={"detail": exc.message})
