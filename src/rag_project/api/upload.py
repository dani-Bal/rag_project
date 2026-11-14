from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
UPLOAD_DIR = Path("data/local/uploads")


router = APIRouter(prefix="/documents", tags=["Documents"])


class UploadResponse(BaseModel):
    document_id: str
    filename: str | None
    size_bytes: int


@router.post(
    "/upload",
    status_code=201,
    responses={
        400: {"description": "Die hochgeladene Datei ist leer"},
        413: {"description": "Die Datei ist größer als 20 MB"},
        415: {
            "description": "Dateityp nicht zulässig. Zulässige Dateitypen sind: PDF, DOCX, TXT und Markdown"
        },
    },
)
async def upload_document(file: UploadFile) -> UploadResponse:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Der hochgeladene Dateityp ist unzulässig. Zulässige Dateitypen sind: PDF, DOCX, TXT und MARKDOWN {sorted(ALLOWED_EXTENSIONS)}",
        )
    content = await file.read(MAX_FILE_SIZE + 1)
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Die hochgeladene Datei ist leer. Bitte laden Sie eine Datei mit Inhalt hoch",
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Die hochgeladene Datei ist zu groß. Bitte laden Sie eine kleinere Datei hoch {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )
    document_id = str(uuid4())
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = UPLOAD_DIR / f"{document_id}{extension}"
    target.write_bytes(content)
    return UploadResponse(document_id=document_id, filename=file.filename, size_bytes=len(content))
