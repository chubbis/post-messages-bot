import logging

from asyncpg import PostgresError
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, text

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
                username = EXCLUDED.username,
                is_admin = EXCLUDED.is_admin,
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


class UserToken(Base):
    __tablename__ = "user_token"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    access_token = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    @classmethod
    async def get_token_by_user_id(cls, user_id: int):
        query = f"""
            SELECT access_token
            FROM user_token
            WHERE user_id = $1
        """

        try:
            async with await adb_session() as conn:
                result = await conn.fetchval(query, user_id)
            return result
        except PostgresError as e:
            logging.error("Error get token by user id: %s", e)
            return

    @classmethod
    async def set_token(cls, user_id: int, access_token: str):
        query = f"""
            INSERT INTO user_token (user_id, access_token)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO 
            UPDATE
                SET 
                    access_token = EXCLUDED.access_token,
                    updated_at = CURRENT_TIMESTAMP
            RETURNING *
        """
        try:
            async with await adb_session() as conn:
                result = await conn.fetchrow(query, user_id, access_token)
            return result
        except PostgresError as e:
            logging.error("Error save access_token: %s", e)
            return
