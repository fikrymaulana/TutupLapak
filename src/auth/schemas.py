from pydantic import BaseModel, EmailStr, constr, Field

# Request bodies
class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=32)

class UserCreatePhone(BaseModel):
    phone: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")
    password: constr(min_length=8, max_length=32)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Responses (spec minta string kosong ketika tidak ada)
class UserOut(BaseModel):
    email: str = ""
    phone: str = ""
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    email: str = ""
    phone: str = ""
    token: str
