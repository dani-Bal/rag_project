from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rag_project.api import upload
from rag_project.main import app

client = TestClient(app)


def test_rejects_png() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("bild.png", b"abcTEST", "image/png")},
    )
    assert response.status_code == 415


def test_rejects_empty() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("file.txt", b"", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_successful(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:

    monkeypatch.setattr(upload, "UPLOAD_DIR", tmp_path)
    content = b"test"
    response = client.post(
        "/documents/upload",
        files={"file": ("file.txt", content, "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert "document_id" in body
    assert body["size_bytes"] == len(content)
    saved = list(tmp_path.iterdir())
    assert len(saved) == 1
    assert saved[0].read_bytes() == content
