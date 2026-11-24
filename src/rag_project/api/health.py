from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("health")
def get_api_health() -> str:
    return f"API healthy - {datetime.now().isoformat()}"
