from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge-base"


def load_markdown_file(file_path: Path) -> dict:
    """
    Load a Markdown knowledge-base document.
    """

    content = file_path.read_text(encoding="utf-8")

    return {
        "text": content,
        "metadata": {
            "source": file_path.name,
            "file_path": str(file_path.relative_to(BASE_DIR)),
            "file_type": "markdown",
            "category": file_path.parent.name,
        },
    }


def load_csv_file(file_path: Path) -> list[dict]:
    """
    Load a CSV knowledge-base file.

    Each CSV row becomes one document so structured maintenance
    information can later be embedded and retrieved independently.
    """

    documents = []

    with file_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row_number, row in enumerate(reader, start=1):
            fields = []

            for key, value in row.items():
                if value is not None and str(value).strip():
                    fields.append(f"{key}: {value}")

            text = "\n".join(fields)

            documents.append(
                {
                    "text": text,
                    "metadata": {
                        "source": file_path.name,
                        "file_path": str(file_path.relative_to(BASE_DIR)),
                        "file_type": "csv",
                        "category": file_path.parent.name,
                        "row_number": row_number,
                    },
                }
            )

    return documents


def load_knowledge_base() -> list[dict]:
    """
    Load all supported documents from the knowledge base.
    """

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}"
        )

    documents = []

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() == ".md":
            documents.append(load_markdown_file(file_path))

        elif file_path.suffix.lower() == ".csv":
            documents.extend(load_csv_file(file_path))

    return documents


def chunk_text(
    text: str,
    chunk_size: int = 3000,
    chunk_overlap: int = 500,
) -> list[str]:
    """
    Split Markdown into logical sections.

    A section starts at a level-1 or level-2 heading (# / ##)
    and includes all following content until the next section.
    Smaller ### headings remain inside their parent section.

    This keeps engineering topics such as:

        ## Bearing Wear
        ### Typical indicators
        ### Recommended maintenance

    together in the same retrieval chunk.
    """

    if not text.strip():
        return []

    lines = text.splitlines()

    sections = []
    current_section = []

    for line in lines:

        # Start a new section only at # or ## headings.
        if line.startswith("# ") or line.startswith("## "):

            if current_section:

                section_text = "\n".join(current_section).strip()

                if section_text:
                    sections.append(section_text)

            current_section = [line]

        else:
            current_section.append(line)

    # Add final section.
    if current_section:

        section_text = "\n".join(current_section).strip()

        if section_text:
            sections.append(section_text)

    chunks = []

    for section in sections:

        # Keep the complete logical section together
        # whenever it fits within the target size.
        if len(section) <= chunk_size:

            chunks.append(section)

            continue

        # Very large sections are split with overlap.
        start = 0
        section_length = len(section)

        while start < section_length:

            end = min(
                start + chunk_size,
                section_length,
            )

            chunk = section[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= section_length:
                break

            start = end - chunk_overlap

    return chunks


def prepare_documents() -> list[dict]:
    """
    Load the knowledge base and convert documents into
    embedding-ready chunks with metadata.
    """

    source_documents = load_knowledge_base()
    chunked_documents = []

    for document in source_documents:
        chunks = chunk_text(document["text"])

        for chunk_index, chunk in enumerate(chunks):
            metadata = document["metadata"].copy()

            metadata["chunk_index"] = chunk_index

            chunked_documents.append(
                {
                    "text": chunk,
                    "metadata": metadata,
                }
            )

    return chunked_documents


if __name__ == "__main__":
    documents = load_knowledge_base()
    chunks = prepare_documents()

    print(f"Knowledge-base documents: {len(documents)}")
    print(f"Prepared chunks: {len(chunks)}")

    print("\nSample chunk:")

    if chunks:
        print("-" * 60)
        print(chunks[0]["text"][:1000])
        print("-" * 60)
        print(chunks[0]["metadata"])
