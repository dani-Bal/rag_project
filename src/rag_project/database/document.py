from dataclasses import dataclass

from .metadata import Metadata


@dataclass
class ProcessedDocument:
    content: str
    metadata: Metadata
    original_file: bytes | None = None
