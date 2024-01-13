import logging

from asyncpg import PostgresError
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    text,
)

from storages.pg import adb_session
from storages.pg_sync import Base


class ForwardedMessage(Base):
    __tablename__ = "forwarded_messages"

    id = Column(Integer, primary_key=True)

    from_chat_id = Column(BigInteger, nullable=False)
    from_user = Column(BigInteger, nullable=False)
    from_message_id = Column(BigInteger, unique=True)

    to_chat_id = Column(BigInteger, nullable=False)
    to_chat_message_id = Column(BigInteger)

    model_type = Column(String, nullable=False)
    message_text = Column(String)
    file_id = Column(String)
    entities = Column(JSON)

    is_private = Column(Boolean)
    is_deleted = Column(Boolean)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "from_chat_id",
            "from_message_id",
            name="unq_messages_from_chat_id_from_message_id",
        ),
    )

    @classmethod
    async def save_message(
        cls,
        from_chat_id: int,
        from_user: int,
        to_chat_id: int,
        from_message_id: int,
        to_chat_message_id: int,
        is_private: bool,
        model_type: str,
        message_text: str,
        file_id: str | None,
        entities: str,
    ) -> int:
        """
        Save message after that has been forwarded
        :param from_chat_id: int - Chat from message forward
        :param from_user: User sent message
        :param to_chat_id: To what Group post the message
        :param is_private: Is message private
        :param to_chat_message_id: forward message id in channel
        :param from_message_id: message id from chat, where message was sent
        :param model_type: str message model type
        :param message_text: str message text or caption
        :param file_id: str file id from message
        :param entities: str JSON hashtags position in text
        :return:
        """
        query = """
            INSERT INTO forwarded_messages
                (
                    from_chat_id, 
                    from_user, 
                    to_chat_id, 
                    from_message_id, 
                    to_chat_message_id, 
                    is_private, 
                    updated_at, 
                    is_deleted,
                    model_type,
                    message_text,
                    file_id,
                    entities
                )
            VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP, FALSE, $7, $8, $9, $10)
            ON CONFLICT ON CONSTRAINT unq_messages_from_chat_id_from_message_id DO UPDATE
            SET 
                updated_at = CURRENT_TIMESTAMP, 
                is_deleted = FALSE,
                to_chat_id = $3,
                to_chat_message_id = $5,
                message_text = $8,
                file_id = $9,
                entities = $10
            RETURNING to_chat_message_id
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    from_chat_id,
                    from_user,
                    to_chat_id,
                    from_message_id,
                    to_chat_message_id,
                    is_private,
                    model_type,
                    message_text,
                    file_id,
                    entities,
                )
            return result["to_chat_message_id"]
        except PostgresError as e:
            logging.error("Error Save forwarded message: %s", e)
            return 0

    @classmethod
    async def get_message(cls, from_message_id: int, from_chat_id: int) -> dict:
        query = """
            SELECT to_chat_message_id, is_deleted, to_chat_id
            FROM forwarded_messages
            WHERE from_message_id = $1
                AND from_chat_id = $2
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    from_message_id,
                    from_chat_id,
                )
            if not result:
                return dict()

            return dict(result)
        except PostgresError as e:
            logging.error("Error Save forwarded message: %s", e)
            return dict()

    @classmethod
    async def get_message_by_id(cls, message_id: int) -> dict:
        query = """
            SELECT *
            FROM forwarded_messages
            WHERE id = $1
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    message_id,
                )
            if not result:
                return dict()

            return dict(result)
        except PostgresError as e:
            logging.error("Something went wrong with DB (get_message_by_id): %s", e)
            return dict()

    @classmethod
    async def delete_with_message_id(
        cls, from_message_id: int, from_chat_id: int
    ) -> int | None:
        query = """
            UPDATE forwarded_messages
            SET is_deleted = TRUE,
                updated_at = CURRENT_TIMESTAMP
            WHERE from_message_id = $1
                AND from_chat_id = $2
            RETURNING to_chat_message_id
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    from_message_id,
                    from_chat_id,
                )
            if not result:
                return
            return result.get("to_chat_message_id")
        except PostgresError as e:
            logging.error("Error Delete forwarded message: %s", e)
            return
