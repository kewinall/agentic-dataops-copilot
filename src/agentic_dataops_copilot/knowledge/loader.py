from importlib.resources import files

from .schema import KnowledgeDocument


def _parse_frontmatter(raw: str, source: str) -> KnowledgeDocument:
    if not raw.startswith("---"):
        raise ValueError(f"Knowledge document is missing frontmatter: {source}")

    parts = raw.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid frontmatter: {source}")

    metadata: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()

    document_id = metadata.get("id")
    title = metadata.get("title")
    if not document_id or not title:
        raise ValueError(f"Knowledge document requires id and title: {source}")

    tags = tuple(
        item.strip().lower()
        for item in metadata.get("tags", "").split(",")
        if item.strip()
    )
    return KnowledgeDocument(
        id=document_id,
        title=title,
        source=metadata.get("source", source),
        content=parts[2].strip(),
        tags=tags,
    )


def load_builtin_documents() -> list[KnowledgeDocument]:
    directory = files("agentic_dataops_copilot").joinpath("knowledge", "documents")
    documents = []
    for resource in sorted(directory.iterdir(), key=lambda item: item.name):
        if resource.name.endswith(".md"):
            documents.append(_parse_frontmatter(resource.read_text("utf-8"), resource.name))
    return documents
