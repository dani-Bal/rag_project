from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

router = APIRouter(prefix="/documents", tags=["Documents"])
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload")
async def upload_document(file: UploadFile) -> dict[str, str | None]:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Der hochgeladene Dateityp ist unzulässig {sorted(ALLOWED_EXTENSIONS)}",
        )
    content = await file.read()
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
    return {"filename": file.filename}
