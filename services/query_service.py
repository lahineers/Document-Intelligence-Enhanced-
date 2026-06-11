from sqlmodel import Session

from models.query import Query
from schemas.query import QueryCreate


class QueryService:

    @staticmethod
    def create_query(
        query_data: QueryCreate,
        session: Session
    ):

        query = Query(
            **query_data.model_dump()
        )

        session.add(query)

        session.commit()

        session.refresh(query)

        return query