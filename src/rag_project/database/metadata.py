from dataclasses import dataclass
from datetime import datetime


@dataclass
class Metadata:
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: str | None = None
    pdf_created_at: datetime | None = None
    page_count: int | None = None
    file_size_bytes: int | None = None
