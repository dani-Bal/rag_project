from fastapi.testclient import TestClient

from rag_project.main import app

client = TestClient(app)


def test_valid_question() -> None:
    response = client.post("/questions", json={"question": "Warum ist die Banane krumm?"})
    assert response.status_code == 200
    assert "answer" in response.json()


def test_rejects_empty_question() -> None:
    response = client.post(
        "/questions",
        json={"question": ""},
    )
    assert response.status_code == 422
