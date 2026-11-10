from .metadata import Metadata


class Document:
    def __init__(
        self, content: str, metadata: Metadata, original_file: bytes | None = None
    ) -> None:
        self.content = content
        self.metadata = metadata
        self.original_file = original_file


if __name__ == "__main__":
    meta1 = Metadata("Mein PDF1", "Max", "KI", "RAG", None, 20, 50000)

    # Nur Titel und Autor bekannt
    meta2 = Metadata(title="Mein PDF2", author="Max")

    # Keine Metadaten bekannt
    meta3 = Metadata()
    print("Meta 1 Titel: ", meta1.title)
    print("Meta 2 Titel: ", meta2.title)
    print("Meta 3 Titel: ")
