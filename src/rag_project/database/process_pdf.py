# Autor: Carsten Ostlender, 2026
# todo: Unittests
import re
from io import BytesIO

from ftfy import fix_text
from pypdf import PdfReader

from .document import Document
from .metadata import Metadata


# Für alle: Verschiedene .doc Dokumente raussuchen und hochladen
# Weitere Verarbeitungsschritte?
def process_pdf(pdf_data: bytes) -> Document:

    reader = PdfReader(BytesIO(pdf_data))
    text = ""
    page_texts: list[str] = []
    # todo: Tabellenextraktion?

    for page in reader.pages:
        page_texts.append(page.extract_text() or "")

    text = "\n".join(page_texts)
    # Unicode Fehler korrigieren
    # print("Vor dem Fix: " + text)

    text = fix_text(text)
    metadata = get_pdf_metadata(reader, len(pdf_data))
    # Tabelle extrahieren

    # print("Nach  dem Fix: " + text)
    document = Document(text, metadata, pdf_data)

    return document


def get_pdf_metadata(reader: PdfReader, file_size: int) -> Metadata:
    info = reader.metadata

    metadata = Metadata(
        title=info.title if info else None,
        author=info.author if info else None,
        subject=info.subject if info else None,
        keywords=info.get("/Keywords") if info else None,
        pdf_created_at=info.creation_date if info else None,
        page_count=len(reader.pages),
        file_size_bytes=file_size,
    )

    return metadata


def process_text(text: str) -> str:
    # Unicode Fehler korrigieren
    text = fix_text(text)

    # Worttrennungen korregieren:
    text = re.sub(r"(?<=[A-Za-zÄÖÜäöüß])-\n(?=[a-zäöü])", "", text)
    # Absätze entfernen
    text = re.sub(r"\n(?:[ \t]*\n)+", "\n\n", text)

    # Überflüssige Leerzeichen  Entfernen
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text
