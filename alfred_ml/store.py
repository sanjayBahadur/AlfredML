import chromadb
from chromadb.config import Settings

def open_store(db_dir: str, collection_name: str):
    client = chromadb.PersistentClient(
        path=db_dir,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(name=collection_name)
    return collection
