import hashlib
from io import BytesIO
from typing import Tuple, List, cast
from PIL import Image, ImageOps
from PIL.Image import Image as PILImage

from .exceptions import BadRequestError
from .constants import ALLOWED_MIME


def generate_cuid() -> str:
    try:
        from cuid2 import Cuid

        return Cuid().generate()
    except Exception:
        import uuid

        return uuid.uuid4().hex


def normalize_mime(mime: str | None) -> str:
    if not mime:
        return ""
    m = mime.lower().strip()
    if m == "image/jpg":
        m = "image/jpeg"
    return m


def ensure_allowed_mime(mime: str) -> None:
    if mime not in ALLOWED_MIME:
        raise BadRequestError("Only jpeg/jpg/png are allowed")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_limited(upload_file, max_bytes: int) -> bytes:
    size = 0
    chunks: List[bytes] = []
    while True:
        chunk = upload_file.file.read(64 * 1024)
        if not chunk:
            break
        size += len(chunk)
        if size > max_bytes:
            raise BadRequestError(f"File size exceeds {max_bytes} bytes")
        chunks.append(chunk)
    return b"".join(chunks)


def detect_image_format(image_bytes: bytes) -> Tuple[str, str]:
    try:
        with Image.open(BytesIO(image_bytes)) as im:
            pil_format = (im.format or "").upper()  # "JPEG"/"JPG"/"PNG"/""
            if pil_format in ("JPEG", "JPG"):
                pil_format = "JPEG"  # normalisasi
                mime = "image/jpeg"
            elif pil_format == "PNG":
                mime = "image/png"
            else:
                raise BadRequestError("Only jpeg/jpg/png are allowed")
    except BadRequestError:
        raise
    except Exception:
        raise BadRequestError("Invalid or corrupted image")
    return pil_format, mime


def make_thumbnail_jpeg_under_limit(
    image_bytes: bytes, target_bytes: int, max_w: int, max_h: int
) -> bytes:
    """
    Konversi thumbnail ke JPEG, turunkan dimensi/quality sampai <= target_bytes.
    """
    try:
        im = cast(PILImage, Image.open(BytesIO(image_bytes)))
        if im is None:
            raise BadRequestError("Invalid or corrupted image")
        try:
            # Hilangkan EXIF & ensure RGB
            im = cast(PILImage, ImageOps.exif_transpose(im))
            if im.mode not in ("RGB", "L"):
                im = cast(PILImage, im.convert("RGB"))

            # Resize clamp
            im.thumbnail((max_w, max_h))  # in-place

            quality = 85
            min_quality = 35
            step = 7

            while True:
                out = BytesIO()
                im.save(out, format="JPEG", quality=quality, optimize=True)
                data = out.getvalue()
                if len(data) <= target_bytes or quality <= min_quality:
                    return data
                quality = max(min_quality, quality - step)

                # Jika masih kebesaran di min_quality, kecilkan dimensi lagi 15% lalu ulang
                if quality == min_quality and len(data) > target_bytes:
                    w, h = im.size
                    nw, nh = max(1, int(w * 0.85)), max(1, int(h * 0.85))
                    if (nw, nh) == im.size or nw < 8 or nh < 8:
                        return data
                    im = cast(PILImage, im.resize((nw, nh)))
                    quality = 75
        finally:
            try:
                im.close()
            except Exception:
                pass
    except BadRequestError:
        raise
    except Exception as e:
        raise BadRequestError("Failed to process image") from e
