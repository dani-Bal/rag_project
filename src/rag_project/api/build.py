from fastapi import FastAPI

from rag_project.api.questions import router as question_router
from rag_project.api.upload import router as upload_router


def build_app() -> FastAPI:
    app = FastAPI(title="RAG Project")
    app.include_router(router=question_router)
    app.include_router(router=upload_router)
    return app
