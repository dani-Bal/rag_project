from fastapi.testclient import TestClient

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
