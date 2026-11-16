from dataclasses import dataclass

from .metadata import Metadata


@dataclass
class Document:
    content: str
    metadata: Metadata
    original_file: bytes | None = None
