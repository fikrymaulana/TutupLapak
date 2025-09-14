# src/main.py
import os
import subprocess
from fastapi import FastAPI
from src.files.router import router as files_router
from fastapi.middleware.cors import CORSMiddleware
from src.auth.router import router as auth_router  # has prefix="/v1"
from src.users.router import router as users_router  # has prefix="/v1"

app = FastAPI(
    title="TutupLapak API",
    version="1.0.0",
    description="TutupLapak API - Authentication, Users, Files service",
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

@app.on_event("startup")
def run_migrations():
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        if result.returncode == 0:
            print("Migrations applied successfully")
        else:
            print(f"Migration failed: {result.stderr}")
    except Exception as e:
        print(f"Error running migrations: {e}")

app.include_router(auth_router)   # no extra prefix here
app.include_router(users_router)  # no extra prefix here
app.include_router(files_router)

# CORS middleware for cross-service compatibility with Go services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to TutupLapak"}
