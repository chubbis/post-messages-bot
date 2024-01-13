import json
import logging

from asyncpg import PostgresError
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    text,
)

from storages.pg import adb_session
from storages.pg_sync import Base


class Hashtags(Base):
    __tablename__ = "hashtag"

    id = Column(Integer, primary_key=True)

    from_chat_id = Column(BigInteger, nullable=False)
    to_chat_id = Column(BigInteger, nullable=False)
    hashtag_name = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        default=text("CURRENT_TIMESTAMP"),
    )
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "from_chat_id",
            "hashtag_name",
            name="unq_hashtags_from_chat_id_to_chat_id_hashtag_name",
        ),
    )

    @classmethod
    async def save_hashtag(
        cls,
        from_chat_id: int,
        to_chat_id: int,
        hashtag_name: str,
    ) -> int:
        """
        Save message after that has been forwarded
        :param from_chat_id: int - Chat from message forward
        :param to_chat_id: To what Group post the message
        :param hashtag_name: str Hashtag name
        :return:
        """
        query = """
            INSERT INTO hashtag
                (
                    from_chat_id, 
                    to_chat_id, 
                    hashtag_name,
                )
            VALUES ($1, $2, $3)
            ON CONFLICT ON CONSTRAINT unq_hashtags_from_chat_id_to_chat_id_hashtag_name 
            DO UPDATE
            SET
                to_chat_id $2
            RETURNING id
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    from_chat_id,
                    to_chat_id,
                    hashtag_name,
                )
            return result["id"]
        except PostgresError as e:
            logging.error("Error Save hashtag: %s", e)
            return 0

    @classmethod
    async def get_hashtags(cls) -> dict:
        query = """
            SELECT
                from_chat_id,
                jsonb_object_agg(hashtag_name, to_chat_id) AS hashtag_info
            FROM
                hashtag
            GROUP BY
                from_chat_id;;
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetch(query)
            if not result:
                return dict()
            return {r["from_chat_id"]: json.loads(r["hashtag_info"]) for r in result}
        except PostgresError as e:
            logging.error("Error Save hashtag: %s", e)
            return dict()

    @classmethod
    async def get_to_chat_id(cls, from_chat_id: int, hashtag_name: str) -> int:
        query = """
            SELECT to_chat_id
            FROM hashtag
            WHERE 
                from_chat_id = $1,
                hashtag_name = $2
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    from_chat_id,
                    hashtag_name,
                )
                return result
        except PostgresError as e:
            logging.error("Error Save forwarded message: %s", e)
            return 0

    @classmethod
    async def delete_hashtag(cls, from_chat_id: int, hashtag: int):
        query = """
            DELETE FROM hashtag 
            WHERE from_chat_id = $1
                AND hashtag_name = $2
            RETURNING id
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    from_chat_id,
                    hashtag,
                )
            if not result:
                return 0
            return result.get("id")
        except PostgresError as e:
            logging.error("Error Delete forwarded message: %s", e)
            return 0
