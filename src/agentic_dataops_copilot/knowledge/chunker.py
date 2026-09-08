import re

from .schema import KnowledgeChunk, KnowledgeDocument

HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)


class MarkdownChunker:
    def __init__(self, max_chars: int = 900) -> None:
        self.max_chars = max_chars

    def chunk(self, document: KnowledgeDocument) -> list[KnowledgeChunk]:
        sections = self._sections(document.content)
        chunks: list[KnowledgeChunk] = []
        index = 1

        for section in sections:
            for piece in self._split_long(section):
                content = piece.strip()
                if not content:
                    continue
                chunks.append(
                    KnowledgeChunk(
                        id=f"{document.id}#chunk-{index}",
                        document_id=document.id,
                        title=document.title,
                        source=document.source,
                        content=content,
                        tags=document.tags,
                    )
                )
                index += 1
        return chunks

    @staticmethod
    def _sections(content: str) -> list[str]:
        lines = content.splitlines()
        sections: list[str] = []
        current: list[str] = []

        for line in lines:
            if HEADING.match(line) and current:
                sections.append("\n".join(current))
                current = [line]
            else:
                current.append(line)

        if current:
            sections.append("\n".join(current))
        return sections

    def _split_long(self, text: str) -> list[str]:
        if len(text) <= self.max_chars:
            return [text]

        paragraphs = [item.strip() for item in text.split("\n\n") if item.strip()]
        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            candidate = paragraph if not current else f"{current}\n\n{paragraph}"
            if len(candidate) <= self.max_chars:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = paragraph

        if current:
            chunks.append(current)
        return chunks
