import logging

from asyncpg import PostgresError
from sqlalchemy import ARRAY, BigInteger, Column, DateTime, Integer, String, text

from storages.pg import adb_session
from storages.pg_sync import Base


class LastGroupMediaFileIds(Base):
    __tablename__ = "last_group_media_file_ids"

    id = Column(Integer, primary_key=True)

    from_chat_id = Column(BigInteger, nullable=False)
    from_message_id = Column(BigInteger, nullable=False)
    file_ids = Column(ARRAY(String))

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    @classmethod
    async def get_media_group_info(cls, from_chat_id: int, from_message_id: int):
        query = f"""
            SELECT file_ids
            FROM {cls.__tablename__}
            WHERE 
                from_chat_id = $1
                AND from_message_id = $2
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchval(query, from_chat_id, from_message_id)
            return result
        except PostgresError as e:
            logging.error("last_group_media_file_ids: %s", e)

    @classmethod
    async def remove_old_messages(cls, from_chat_id: int, offset: int = 20):
        query = f"""
            DELETE FROM {cls.__tablename__}
            WHERE id IN (
                SELECT id FROM {cls.__tablename__}
                WHERE from_chat_id = $1
                ORDER BY created_at
                OFFSET $2
            )
        """
        try:
            async with await adb_session() as conn:
                await conn.execute(query, from_chat_id, offset)
        except PostgresError as e:
            logging.error("last_group_media_file_ids: remove_old_messages: %s", e)

    @classmethod
    async def create_new_message(
        cls, from_chat_id: int, from_message_id: int, file_ids: list[str]
    ):
        await cls.remove_old_messages(from_chat_id=from_chat_id)
        query = f"""
            INSERT INTO {cls.__tablename__} (from_chat_id, from_message_id, file_ids)
            VALUES ($1, $2, $3)
        """
        try:
            async with await adb_session() as conn:
                await conn.execute(query, from_chat_id, from_message_id, file_ids)
        except PostgresError as e:
            logging.error("last_group_media_file_ids:create_new_message : %s", e)
