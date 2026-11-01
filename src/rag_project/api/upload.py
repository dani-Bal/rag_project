from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

router = APIRouter(prefix="/documents", tags=["Documents"])
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}


@router.post("/upload")
async def upload_document(file: UploadFile) -> dict[str, str | None]:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Der hochgeladene Dateityp ist unzulässig {sorted(ALLOWED_EXTENSIONS)}",
        )

    return {"filename": file.filename}
