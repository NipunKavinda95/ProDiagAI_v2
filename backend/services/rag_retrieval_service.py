import os
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "prodiag-ai",
)

PINECONE_NAMESPACE = os.getenv(
    "PINECONE_NAMESPACE",
    "prodiag",
)


if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not configured.")

if not PINECONE_API_KEY:
    raise RuntimeError("PINECONE_API_KEY is not configured.")


openai_client = OpenAI(api_key=OPENAI_API_KEY)

pinecone_client = Pinecone(api_key=PINECONE_API_KEY)


def create_query_embedding(query: str) -> List[float]:
    """
    Convert an engineer's question into an embedding.
    """

    response = openai_client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=query,
    )

    return response.data[0].embedding


def retrieve_knowledge(
    query: str,
    top_k: int = 5,
) -> List[Dict]:
    """
    Retrieve the most relevant knowledge-base chunks
    from Pinecone.
    """

    if not query.strip():
        return []

    query_embedding = create_query_embedding(query)

    index = pinecone_client.Index(PINECONE_INDEX_NAME)

    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace=PINECONE_NAMESPACE,
        include_metadata=True,
    )

    matches = []

    for match in result.matches:
        metadata = match.metadata or {}

        matches.append(
            {
                "id": match.id,
                "score": float(match.score),
                "text": metadata.get("text", ""),
                "source": metadata.get(
                    "source",
                    "unknown",
                ),
                "category": metadata.get(
                    "category",
                    "unknown",
                ),
                "file_path": metadata.get(
                    "file_path",
                    "",
                ),
                "chunk_index": metadata.get(
                    "chunk_index",
                    0,
                ),
            }
        )

    return matches


def print_results(
    query: str,
    results: List[Dict],
):
    """
    Display retrieval results for testing.
    """

    print("\n" + "=" * 70)
    print("RAG RETRIEVAL TEST")
    print("=" * 70)

    print(f"\nQuery:")
    print(query)

    print(f"\nResults returned: {len(results)}")

    for index, result in enumerate(
        results,
        start=1,
    ):
        print("\n" + "-" * 70)

        print(f"Result #{index}")

        print(f"Score: {result['score']:.4f}")

        print(f"Source: {result['source']}")

        print(f"Category: {result['category']}")

        print(f"Chunk: {result['chunk_index']}")

        print("\nContent:")

        print(result["text"][:1500])


if __name__ == "__main__":

    test_query = "What are the typical indicators " "of bearing wear?"

    results = retrieve_knowledge(
        test_query,
        top_k=5,
    )

    print_results(
        test_query,
        results,
    )
