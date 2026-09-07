import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "prodiag_ai")
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"


if not PINECONE_API_KEY:
    raise RuntimeError("PINECONE_API_KEY is not configured.")


pc = Pinecone(api_key=PINECONE_API_KEY)


def list_indexes():
    """
    Return existing Pinecone index names.
    """

    response = pc.list_indexes()

    return [index["name"] for index in response]


def get_index():
    """
    Return the configured Pinecone index.
    """

    return pc.Index(PINECONE_INDEX_NAME)


def create_index_if_missing(dimension: int):
    """
    Create the ProDiag Pinecone index if it does not exist.

    The dimension must match the embedding model output.
    """

    existing_indexes = list_indexes()

    if PINECONE_INDEX_NAME in existing_indexes:
        print(f"Pinecone index already exists: " f"{PINECONE_INDEX_NAME}")

        index = get_index()

        description = pc.describe_index(PINECONE_INDEX_NAME)

        existing_dimension = description.dimension

        print(f"Index dimension: {existing_dimension}")
        print(f"Expected dimension: {dimension}")

        if existing_dimension != dimension:
            raise RuntimeError(
                f"Pinecone dimension mismatch. "
                f"Existing index={existing_dimension}, "
                f"embedding dimension={dimension}."
            )

        print("Pinecone index dimension verified.")

        return index

    print(f"Creating Pinecone index: " f"{PINECONE_INDEX_NAME}")

    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=PINECONE_CLOUD,
            region=PINECONE_REGION,
        ),
    )

    print("Pinecone index creation requested.")

    return get_index()


if __name__ == "__main__":
    print("Existing Pinecone indexes:")

    for name in list_indexes():
        print(f"- {name}")

    print()
    print("This script requires the embedding dimension " "to create a new index.")
