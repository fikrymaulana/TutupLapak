
# src/users/service.py
from pydantic import BaseModel, Field
from typing import Optional

from src.files.models import FileObject



class UpdateProfileRequest(BaseModel):
    fileId: Optional[str] = Field(default=None)
    bankAccountName: Optional[str] = ""
    bankAccountHolder: Optional[str] = ""
    bankAccountNumber: Optional[str] = ""

class LinkPhoneRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")

class LinkEmailRequest(BaseModel):
    email: str

class UserProfileResponse(BaseModel):
    email: str = ""
    phone: str = ""
    fileId: str = ""
    fileUri: str = ""
    fileThumbnailUri: str = ""
    bankAccountName: str = ""
    bankAccountHolder: str = ""
    bankAccountNumber: str = ""

    class Config:
        from_attributes = True



