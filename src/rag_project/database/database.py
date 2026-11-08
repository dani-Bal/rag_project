#Autor: Carsten Ostlender, 2026
#TODO: Unit Tests
#Verbindung aus Datei lesen (verschlüsselt)

#from rag_project.config import get_settings
import psycopg
from enum import StrEnum
from document import Document
from metadata import Metadata
from chonkie import (
    TokenChunker,
    SentenceChunker,
    RecursiveChunker,
    SemanticChunker,
    LateChunker
)

class ChunkingStrategy(StrEnum):
    FIXED_SIZE = "fixed_size"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    LATE = "late"
    SENTENCE = "sentence"

token_count = 35
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
threshold_length = 0.65

text = (
    "Python ist eine Programmiersprache. Sie wird häufig für KI verwendet. "
    "Machine Learning erkennt Muster in Daten. Neuronale Netze lernen aus Beispielen. "
    "PostgreSQL ist eine relationale Datenbank. Mit pgvector kann man Embeddings speichern. "
    "SQL ermöglicht das Abfragen von Daten. Datenbanken sind für RAG-Systeme wichtig. "
    "Fußball wird von zwei Mannschaften gespielt. Bayern München spielt in der Bundesliga. "
    "Ein Fußballspiel dauert normalerweise 90 Minuten. "
    "Astronomie beschäftigt sich mit Sternen und Planeten. "
    "Die Erde umkreist die Sonne. Der Mond umkreist die Erde."
)

def connectDatabase():
    settings = get_settings()

    return psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )

def insert_document(document_name, document, strategy):

#Unsinnige und leere Eingaben abfangen
    if not document_name or not document_name.strip():
        raise ValueError("Dokumentname darf nicht leer sein.")

    if document is None:
        raise ValueError("Dokument muss verhanden sein.")

    if document.content is None or document.metadata is None:
        raise ValueError("Kein Dokumentinhalt oder Metadaten vorhanden.")

    if not strategy:
        raise ValueError("Strategie muss vorhanden sein.")
    
    # creating a cursor object
    content = document.content


    parameters = "{}"
    embedding_model = "TEST"   
    chunks = []
    #Chunking Strategie auswählen
    try:
        match strategy:
            case ChunkingStrategy.FIXED_SIZE:
                chunker = TokenChunker(tokenizer="word", chunk_size=token_count, chunk_overlap=5)
                chunks = chunker.chunk(content)
                print("Fixed size strategy")
            case ChunkingStrategy.SENTENCE:
                chunker = SentenceChunker(tokenizer="word", chunk_size=token_count)
                chunks = chunker.chunk(content)
                print("Sentence strategy")
            case ChunkingStrategy.RECURSIVE:
                chunker = RecursiveChunker(tokenizer="word", chunk_size=token_count)
                chunks = chunker.chunk(content)
                print("Recursive strategy")
            case ChunkingStrategy.SEMANTIC:
                chunker = SemanticChunker(embedding_model=MODEL_NAME, chunk_size=token_count, threshold=threshold_length)
                chunks = chunker.chunk(content)
                print("Semantic strategy")
            case ChunkingStrategy.LATE:
                chunker = LateChunker(embedding_model=MODEL_NAME,chunk_size=token_count)
                chunks = chunker.chunk(content)
                print("Late strategy")
            case _:
                print("Bitte geben Sie eine gültige Strategie an.")
                raise Exception('This is the exception you expect to handle')
    

    except Exception as error:
        print("Es gab einen Fehler: " + repr(error))
    try:
        with connectDatabase() as connection:
            cursor = connection.cursor()
            #Daten in die Datenbank eintragen
            #KI-generiertes SQL statement
            cursor.execute("""
                        INSERT INTO pdf_metadata (
                        title, author, subject, keywords,
                        pdf_created_at, page_count, file_size_bytes
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                        """, (
                        document.metadata.title,
                        document.metadata.author,
                        document.metadata.subject,
                        document.metadata.keywords,
                        document.metadata.pdf_created_at,
                        document.metadata.page_count,
                        document.metadata.file_size_bytes
                        ))
            
            metadata_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO documents (filename, content,metadata_id) VALUES (%s, %s, %s) RETURNING id;",(document_name, content, metadata_id)) 
            document_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO chunking_runs (document_id, strategy, parameters, embedding_model) VALUES (%s, %s, %s, %s) RETURNING id;",(document_id, strategy, parameters, embedding_model))
            run_id = cursor.fetchone()[0]
            #schleife über alle chunks
            for i in range (0, len(chunks),1):
                cursor.execute("INSERT INTO chunks (run_id, chunk_index, content, token_count, embedding) VALUES (%s, %s, %s, %s, %s)",(run_id, i, chunks[i].text, chunks[i].token_count, None))

            

    except Exception:
        print("Fehler beim INSERT.")
        raise
    print("Insert erfolgreich!")

#KI Generiert Verbindung testen
def testConnection():
    try:
        with connectDatabase() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database(), version()")
                result = cursor.fetchone()
                print("Verbindung erfolgreich!")
                print("Datenbank:", result[0])
                print("PostgreSQL:", result[1])

    except psycopg.Error as error:
        print("Datenbankverbindung fehlgeschlagen:", error)

if __name__ == "__main__":
    #testConnection()
    meta1 = Metadata()
    doc1 = Document(text, meta1)
    insert_document("test3.pdf", doc1, ChunkingStrategy.FIXED_SIZE)
    #insert_document("", None, None)
    #insert_document("test3.pdf", text, ChunkingStrategy.SEMANTIC)
    #insert_document("test3.pdf", text, ChunkingStrategy.SENTENCE)
    #insert_document("test3.pdf", text, ChunkingStrategy.RECURSIVE)
    #insert_document("test3.pdf", text, ChunkingStrategy.LATE)

