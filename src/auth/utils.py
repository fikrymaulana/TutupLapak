from passlib.context import CryptContext

# Membuat konteks untuk hashing, kita pakai algoritma bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Fungsi untuk memverifikasi password asli dengan hash di database."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Fungsi untuk membuat hash dari password."""
    return pwd_context.hash(password)