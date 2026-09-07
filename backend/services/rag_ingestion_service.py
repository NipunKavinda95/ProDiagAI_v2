import os
import sys
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

from rag_service import prepare_documents
from pinecone_service import create_index_if_missing

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not configured.")


openai_client = OpenAI(api_key=OPENAI_API_KEY)


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate OpenAI embeddings for text."""

    if not texts:
        return []

    response = openai_client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=texts,
    )

    return [item.embedding for item in response.data]


def build_vectors(documents: List[Dict]) -> List[Dict]:
    """Convert prepared documents into Pinecone vectors."""

    texts = [document["text"] for document in documents]

    embeddings = create_embeddings(texts)

    vectors = []

    for index, (document, embedding) in enumerate(zip(documents, embeddings)):
        metadata = document["metadata"].copy()
        metadata["text"] = document["text"]

        vector_id = f"{metadata['source']}" f"-{metadata['chunk_index']}"

        vectors.append(
            {
                "id": vector_id,
                "values": embedding,
                "metadata": metadata,
            }
        )

    return vectors


def ingest_knowledge_base():
    """Load, embed and upload the complete knowledge base."""

    print("=" * 60)
    print("ProDiag AI V2 - RAG Knowledge Base Ingestion")
    print("=" * 60)

    print("\n[1/4] Loading knowledge base...")

    documents = prepare_documents()

    if not documents:
        raise RuntimeError("No knowledge-base chunks found.")

    print(f"Prepared chunks: {len(documents)}")

    print("\n[2/4] Creating OpenAI embeddings...")

    vectors = build_vectors(documents)

    if not vectors:
        raise RuntimeError("No vectors were generated.")

    embedding_dimension = len(vectors[0]["values"])

    print(f"Embedding model: {OPENAI_EMBEDDING_MODEL}")

    print(f"Embedding dimension: {embedding_dimension}")

    print("\n[3/4] Verifying Pinecone index...")

    index = create_index_if_missing(dimension=embedding_dimension)

    print("\n[4/4] Uploading vectors to Pinecone...")

    namespace = os.getenv(
        "PINECONE_NAMESPACE",
        "prodiag",
    )

    index.upsert(
        vectors=vectors,
        namespace=namespace,
    )

    print("\n" + "=" * 60)
    print("RAG INGESTION COMPLETED")
    print("=" * 60)

    print(f"Index: {os.getenv('PINECONE_INDEX_NAME', 'prodiag_ai')}")
    print(f"Namespace: {namespace}")
    print(f"Vectors uploaded: {len(vectors)}")
    print(f"Dimension: {embedding_dimension}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        ingest_knowledge_base()

    except Exception as error:
        print("\n[RAG INGESTION ERROR]")
        print(error)
        sys.exit(1)
