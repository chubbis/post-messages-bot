from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)

from storages.pg import adb_session
from storages.pg_sync import Base


class Chat(Base):
    __tablename__ = "chat"

    id = Column(BigInteger, primary_key=True)
    chat_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    username = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    @classmethod
    async def get_chat_by_id(cls, chat_id: int):
        query = f"""
            SELECT *
            FROM {cls.__tablename__}
            WHERE
                id = $1
        """

        async with await adb_session() as conn:
            result = await conn.fetch(query, chat_id)

        return result

    @classmethod
    async def set_chat(cls, chat_id: int, chat_type: str, title: str, username: str):
        query = f"""
        INSERT INTO {cls.__tablename__}
            (
                id,
                chat_type,
                title,
                username
            )
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id)
            DO UPDATE
            SET chat_type = $2, title = $3, username = $4
            RETURNING *
        """
        async with await adb_session() as conn:
            result = await conn.fetch(query, chat_id, chat_type, title, username)

        return result


class ChatSettings(Base):
    __tablename__ = "chat_settings"

    id = Column(Integer, primary_key=True)
    variable_name = Column(String, nullable=False)
    value = Column(String, nullable=False)

    chat_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "chat_id",
            "variable_name",
            name="unq_messages_chat_id_variable_name",
        ),
    )

    @classmethod
    async def get(cls, variable_name: str, chat_id: int) -> str:
        query = f"""
            SELECT value
            FROM {cls.__tablename__}
            WHERE
                variable_name = $1
                AND chat_id = $2
        """

        async with await adb_session() as conn:
            result = await conn.fetchval(query, variable_name, chat_id)

        return result

    @classmethod
    async def set(
        cls, variable_name: str, value: str, chat_id: int, user_id: int
    ) -> str:
        query = f"""
            INSERT INTO {cls.__tablename__}
            (variable_name, value, chat_id, user_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (chat_id, variable_name) DO
            UPDATE
            SET 
                value = $2, 
                updated_at = CURRENT_TIMESTAMP, 
                user_id = $4
            RETURNING value
        """

        async with await adb_session() as conn:
            result = await conn.fetchval(query, variable_name, value, chat_id, user_id)

        return result
