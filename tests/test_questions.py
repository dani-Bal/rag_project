from collections.abc import Iterator
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from rag_project.api.dependencies import get_agent, get_embedding_client, get_session
from rag_project.main import app

client = TestClient(app)


class FakeAgent:
    def run_sync(self, question: str, deps: object) -> SimpleNamespace:
        return SimpleNamespace(output="Dies ist eine TESTAntwort auf die Frage.")


class FailingAgent:
    def run_sync(self, question: str, deps: object) -> SimpleNamespace:
        raise Exception("Simulierter TESTFehler beim Beantworten der Frage.")


@pytest.fixture(autouse=True)
def override_dependencies() -> Iterator[None]:
    app.dependency_overrides[get_session] = lambda: None
    app.dependency_overrides[get_embedding_client] = lambda: None
    app.dependency_overrides[get_agent] = lambda: FakeAgent()
    yield
    app.dependency_overrides.clear()


def test_valid_question() -> None:
    response = client.post("/questions", json={"question": "Warum ist die Banane krumm?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Dies ist eine TESTAntwort auf die Frage."
    assert body["sources"] == []


def test_rejects_empty_question() -> None:
    response = client.post(
        "/questions",
        json={"question": ""},
    )
    assert response.status_code == 422


def test_returns_500_on_agent_error() -> None:
    app.dependency_overrides[get_agent] = lambda: FailingAgent()
    response = client.post("/questions", json={"question": "Warum ist die Banane krumm?"})
    assert response.status_code == 500
    body = response.json()
    assert (
        body["detail"]
        == "Ein unerwarteter Fehler ist aufgetreten. Versuchen Sie es bitte später erneut."
    )
