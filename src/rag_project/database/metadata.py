from datetime import datetime


class Metadata:
    def __init__(
        self,
        title: str | None = None,
        author: str | None = None,
        subject: str | None = None,
        keywords: str | None = None,
        pdf_created_at: datetime | None = None,
        page_count: int | None = None,
        file_size_bytes: int | None = None,
    ) -> None:
        self.title = title
        self.author = author
        self.subject = subject
        self.keywords = keywords
        self.pdf_created_at = pdf_created_at
        self.page_count = page_count
        self.file_size_bytes = file_size_bytes
