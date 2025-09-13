from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    fileId: str
    fileUri: str
    fileThumbnailUri: str
