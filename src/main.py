from fastapi import FastAPI
from .files.router import router as files_router

app = FastAPI(title="TutupLapak", version="1.0.0")

# TODO: Add feature routers here
# from .auth.router import auth_router
# from .users.router import users_router

# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(files_router, tags=["Files"])


@app.get("/")
def read_root():
    return {"message": "Welcome to TutupLapak"}
