import re

from core.settings import settings


class ChunkingService:

    @staticmethod
    def _is_valid_heading(
        heading: str
    ) -> bool:

        heading = heading.strip()

        if len(heading) < 10:
            return False

        if len(
            heading.split()
        ) < 2:
            return False

        cleaned = (
            heading
            .replace("%", "")
            .replace(".", "")
            .replace("*", "")
            .strip()
        )

        if cleaned.isdigit():
            return False

        return True

    @classmethod
    def _split_by_headings(
        cls,
        markdown_content: str
    ) -> list[dict]:

        pattern = r"^(#{1,2})\s+(.+)$"

        lines = markdown_content.splitlines()

        sections = []

        current_title = "Document Start"

        current_content = []

        for line in lines:

            match = re.match(
                pattern,
                line
            )

            if match:

                candidate_title = (
                    match.group(2)
                    .strip()
                )

                if not cls._is_valid_heading(
                    candidate_title
                ):
                    current_content.append(
                        line
                    )

                    continue

                if current_content:

                    content = (
                        "\n".join(
                            current_content
                        ).strip()
                    )

                    if content:
                        sections.append(
                            {
                                "section_title":
                                current_title,

                                "content":
                                content
                            }
                        )

                current_title = (
                    candidate_title
                )

                current_content = []

            else:

                current_content.append(
                    line
                )

        if current_content:

            content = (
                "\n".join(
                    current_content
                ).strip()
            )

            if content:
                sections.append(
                    {
                        "section_title":
                        current_title,

                        "content":
                        content
                    }
                )

        return sections

    @classmethod
    def _overflow_chunk(
        cls,
        text: str
    ) -> list[str]:

        words = text.split()

        chunk_size = (
            settings.chunk_size
        )

        overlap = (
            settings.chunk_overlap
        )

        chunks = []

        start = 0

        while start < len(words):

            end = (
                start
                + chunk_size
            )

            chunk_words = (
                words[start:end]
            )

            chunks.append(
                " ".join(chunk_words)
            )

            if end >= len(words):
                break

            start = (
                end
                - overlap
            )

        return chunks

    @classmethod
    def chunk_document(
        cls,
        markdown_content: str
    ) -> list[dict]:

        sections = (
            cls._split_by_headings(
                markdown_content
            )
        )

        print(
            f"Sections Found: {len(sections)}",
            flush=True
        )

        # Fallback if heading detection fails
        if not sections:

            print(
                "No valid sections found. Using overflow chunking."
            )

            overflow_chunks = (
                cls._overflow_chunk(
                    markdown_content
                )
            )

            results = []

            for index, chunk in enumerate(
                overflow_chunks
            ):

                results.append(
                    {
                        "chunk_index": index,
                        "section_title": "Document",
                        "content": chunk,
                        "chunk_strategy": "fallback_overflow"
                    }
                )

            return results

       

        results = []

        chunk_index = 0

        for section in sections:

            token_count = len(
                section["content"].split()
            )

            if token_count <= (
                settings.chunk_size
            ):

                results.append(
                    {
                        "chunk_index":
                        chunk_index,

                        "section_title":
                        section["section_title"],

                        "content":
                        section["content"],

                        "chunk_strategy":
                        "heading"
                    }
                )

                chunk_index += 1

            else:

                overflow_chunks = (
                    cls._overflow_chunk(
                        section["content"]
                    )
                )

                for chunk in overflow_chunks:

                    results.append(
                        {
                            "chunk_index":
                            chunk_index,

                            "section_title":
                            section["section_title"],

                            "content":
                            chunk,

                            "chunk_strategy":
                            "overflow"
                        }
                    )

                    chunk_index += 1

        return results