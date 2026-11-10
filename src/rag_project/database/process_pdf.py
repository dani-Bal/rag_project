# Autor: Carsten Ostlender, 2026
# todo: Unittests
import os
import re

from ftfy import fix_text
from pypdf import PdfReader

from .document import Document
from .metadata import Metadata


# Für alle: Verschiedene .doc Dokumente raussuchen und hochladen
# Weitere Verarbeitungsschritte?
def process_pdf(pdf_path: str) -> Document:

    reader = PdfReader(pdf_path)
    info = reader.metadata
    text = ""

    # todo: Tabellenextraktion?

    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Unicode Fehler korregieren
    # print("Vor dem Fix: " + text)

    text = fix_text(text)

    # Worttrennungen korregieren:
    text = re.sub(r"(?<=[A-Za-zÄÖÜäöüß])-\n(?=[a-zäöü])", "", text)
    # Absätze entfernen
    text = re.sub(r"\n(?:[ \t]*\n)+", "\n\n", text)

    # Überflüssige Leerzeichen  Entfernen
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # Tabelle extrahieren

    # print("Nach  dem Fix: " + text)

    metadata = Metadata(
        title=info.title if info else None,
        author=info.author if info else None,
        subject=info.subject if info else None,
        keywords=info.get("/Keywords") if info else None,
        pdf_created_at=info.creation_date if info else None,
        page_count=len(reader.pages),
        file_size_bytes=os.path.getsize(pdf_path),
    )
    try:
        with open(pdf_path, "rb") as file:
            pdf_data = file.read()
    except Exception as e:
        print(f"Fehler beim Lesen der PDF-Datei: {e}")
        raise

    document = Document(text, metadata, pdf_data)

    return document


if __name__ == "__main__":
    process_pdf("Test.pdf")
