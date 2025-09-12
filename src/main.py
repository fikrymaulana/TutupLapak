# src/main.py
from fastapi import FastAPI
from src.auth.router import router as auth_router  # has prefix="/v1"
from src.users.router import router as users_router # has prefix="/v1"

app = FastAPI(
    title="TutupLapak API",
    version="1.0.0",
    description="TutupLapak API - Authentication, Users, Files service",
)

app.include_router(auth_router)   # no extra prefix here
app.include_router(users_router)  # no extra prefix here

@app.get("/")
def read_root():
    return {"message": "Welcome to TutupLapak API!"}
