from sqlalchemy import BigInteger, Column, DateTime, Integer, String, text, UniqueConstraint

from storages.pg import adb_session
from storages.pg_sync import Base


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
        query = """
            SELECT value
            FROM chat_settings
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
        query = """
            INSERT INTO chat_settings
            (variable_name, value, chat_id, user_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (chat_id, variable_name) DO
            UPDATE chat_settings
            SET 
                value = $2, 
                updated_at = CURRENT_TIMESTAMP, 
                user_id = $4
            RETURNING value
        """

        async with await adb_session() as conn:
            result = await conn.exexute(query, variable_name, value, chat_id, user_id)

        return result
