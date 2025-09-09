from fastapi import FastAPI
from src.auth.router import router as auth_router

app = FastAPI(
    title="TutupLapak API",
    version="1.0.0",
    description="TutupLapak API - Authentication, Users, Files service"
)

# Global versioning di sini
app.include_router(auth_router, prefix="/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to TutupLapak API!"}
