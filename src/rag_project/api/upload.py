from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(file: UploadFile) -> dict[str, str | None]:
    return {"filename": file.filename}
