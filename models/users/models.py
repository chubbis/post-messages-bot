import logging

from asyncpg import PostgresError
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, text

from storages.pg import adb_session
from storages.pg_sync import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        query = f"""
            SELECT *
            FROM {Users.__tablename__}
            WHERE id = $1
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    user_id,
                )
            return result
        except PostgresError as e:
            logging.error("Error Save forwarded message: %s", e)

    @classmethod
    async def update_or_create_user(
            cls, user_id: int, username: str, is_admin: bool = False
    ):
        query = f"""
            INSERT INTO {Users.__tablename__} (id, username, is_admin)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO
            UPDATE SET
                username = $2,
                is_admin = $3,
                UPDATED_AT = CURRENT_TIMESTAMP
            RETURNING *
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(
                    query,
                    user_id,
                    username,
                    is_admin,
                )
            return result
        except PostgresError as e:
            logging.error("Error Save forwarded message: %s", e)
