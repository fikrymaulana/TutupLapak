from pydantic import BaseModel, constr, Field, EmailStr

class UpdateProfileRequest(BaseModel):
    fileId: str | None = None
    bankAccountName: constr(min_length=4, max_length=32)
    bankAccountHolder: constr(min_length=4, max_length=32)
    bankAccountNumber: constr(min_length=4, max_length=32)

class UserProfileResponse(BaseModel):
    email: str = ""
    phone: str = ""
    fileId: str = ""
    fileUri: str = ""            # placeholder
    fileThumbnailUri: str = ""   # placeholder
    bankAccountName: str = ""
    bankAccountHolder: str = ""
    bankAccountNumber: str = ""
    
class LinkPhoneRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")


class LinkEmailRequest(BaseModel):
    email: EmailStr
