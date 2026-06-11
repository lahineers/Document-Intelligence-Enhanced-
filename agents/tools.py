from services.comparison_service import (
    ComparisonService
)


class Tools:

    _session = None

    @classmethod
    def set_session(
        cls,
        session
    ):
        cls._session = session

    @classmethod
    def compare_documents(
        cls,
        question: str,
        document_ids: list[str]
    ):

        return (
            ComparisonService
            .compare_documents(
                question=question,
                document_ids=document_ids,
                session=cls._session
            )
        )