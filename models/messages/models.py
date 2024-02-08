import logging
from typing import Optional

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

from models.chats.models import Chat
from models.users.models import Users
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
        query = f"""
            INSERT INTO {cls.__tablename__}
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
        query = f"""
            SELECT to_chat_message_id, is_deleted, to_chat_id
            FROM {cls.__tablename__}
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
        query = f"""
            SELECT *
            FROM {cls.__tablename__}
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
    async def get_messages(
            cls,
            from_chat_ids: list[int] = None,
            from_chat_usernames: list[str] = None,
            to_chat_ids: list[int] = None,
            to_chat_usernames: list[str] = None,
            from_user_ids: list = None,
            from_user_usernames: list[str] = None,
            order_by: str = "",
            order_type_desc: bool = False,
            fields: list[str] = None,
            limit: int = 0,
            offset: int = 0,
            only_count: bool = False,
            has_text: bool = True,
    ) -> list:
        if only_count:
            fields = "count(*)"
            limit = 0
            offset = 0
        else:
            fields = cls._sanitize_user_input_columns(
                fields, default_value=f"{cls.__tablename__}.*"
            )

        query, params = cls._prepare_query_conditions(
            fields=fields,
            table_name=cls.__tablename__,
            from_chat_ids=from_chat_ids,
            from_chat_usernames=from_chat_usernames,
            to_chat_ids=to_chat_ids,
            to_chat_usernames=to_chat_usernames,
            from_user_ids=from_user_ids,
            from_user_usernames=from_user_usernames,
            order_by=order_by,
            order_type_desc=order_type_desc,
            limit=limit,
            offset=offset,
            only_count=only_count,
            has_text=has_text,
        )
        try:
            async with await adb_session() as conn:
                result = await conn.fetch(
                    query,
                    *params,
                )
            return result
        except PostgresError as e:
            logging.error("Error get forwarded message: %s", e)
            return []

    @classmethod
    async def delete_with_message_id(
        cls, from_message_id: int, from_chat_id: int
    ) -> int | None:
        query = f"""
            UPDATE {cls.__tablename__}
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

    @classmethod
    def _prepare_query_conditions(
            cls,
            table_name,
            fields: str,
            from_chat_ids: list[int] = None,
            from_chat_usernames: list[str] = None,
            to_chat_ids: list[int] = None,
            to_chat_usernames: list[str] = None,
            from_user_ids: list = None,
            from_user_usernames: list[str] = None,
            order_by: str = "",
            order_type_desc: bool = False,
            limit: int = 0,
            offset: int = 0,
            only_count: bool = False,
            has_text: bool = True,
    ) -> tuple[str, list]:
        select_part = f"SELECT {fields}"
        if not only_count:
            select_part = (
                    select_part
                    + ","
                    + f"""
                JSON_BUILD_OBJECT(
                    'title', from_chat.title, 
                    'username', from_chat.username, 
                    'id', {table_name}.from_chat_id
                    ) AS from_chat,
                JSON_BUILD_OBJECT(
                    'title', to_chat.title,
                    'username', to_chat.username,
                    'id', {table_name}.to_chat_id
                    ) AS to_chat,
                JSON_BUILD_OBJECT(
                    'username', {Users.__tablename__}.username,
                    'id', {table_name}.from_user
                    ) AS from_user_info
            """
            )

        query = f"""
            {select_part}
            FROM {table_name}
            LEFT JOIN
                {Chat.__tablename__} AS from_chat ON {table_name}.from_chat_id = from_chat.id
            LEFT JOIN
                {Chat.__tablename__} AS to_chat ON {table_name}.to_chat_id = to_chat.id
            LEFT JOIN
                {Users.__tablename__} AS {Users.__tablename__} ON {table_name}.from_user = {Users.__tablename__}.id
        """
        conditions_str, params = cls._prepare_conditions_string_and_params(
            chats_table_name=Chat.__tablename__,
            users_table_name=Users.__tablename__,
            from_chat_ids=from_chat_ids,
            from_chat_usernames=from_chat_usernames,
            to_chat_ids=to_chat_ids,
            to_chat_usernames=to_chat_usernames,
            from_user_ids=from_user_ids,
            from_user_usernames=from_user_usernames,
            has_text=has_text,
        )

        if conditions_str:
            query += f" WHERE {conditions_str}"

        if order_by and not only_count:
            sanitized_order_by = cls._sanitize_user_input_columns(order_by, "")
            if sanitized_order_by:
                query += f" ORDER BY {sanitized_order_by} {'DESC' if order_type_desc else 'ASC'}"

        if limit:
            query += f" LIMIT {limit + 1}"
        if offset:
            query += f" OFFSET {offset}"

        return query, params

    @staticmethod
    def _sanitize_user_input_columns(
            input_columns: list[str] | str | None, default_value: str = "*"
    ) -> str:
        allowed_columns = [column.name for column in ForwardedMessage.__table__.columns]
        for column in ForwardedMessage.__table__.columns:
            allowed_columns.append(column.name)
            allowed_columns.append(f"{ForwardedMessage.__tablename__}.{column.name}")
        for column in Chat.__table__.columns:
            allowed_columns.append(column.name)
            allowed_columns.append(f"{Chat.__tablename__}.{column.name}")
        for column in Users.__table__.columns:
            allowed_columns.append(column.name)
            allowed_columns.append(f"{Users.__tablename__}.{column.name}")
        if input_columns is None:
            input_columns = []
        if isinstance(input_columns, str):
            input_columns = [input_columns]
        columns = []
        for column in input_columns:
            if column in allowed_columns:
                columns.append(column)

        return ", ".join(columns) or default_value

    @staticmethod
    def _prepare_conditions_string_and_params(
            users_table_name: str,
            chats_table_name: str,
            from_chat_ids: list[int] = None,
            from_chat_usernames: list[str] = None,
            to_chat_ids: list[int] = None,
            to_chat_usernames: list[str] = None,
            from_user_ids: list[int] = None,
            from_user_usernames: list[str] = None,
            has_text: bool = True,
    ) -> tuple[str, list]:
        conditions = []
        params = []
        if from_chat_ids:
            params.append(from_chat_ids)
            conditions.append(f"from_chat_id = ANY(${len(params)})")
        if from_chat_usernames:
            params.append(from_chat_usernames)
            conditions.append(f"{chats_table_name}.username = ANY(${len(params)})")
        if to_chat_ids:
            params.append(to_chat_ids)
            conditions.append(f"to_chat_id = ANY(${len(params)})")
        if to_chat_usernames:
            params.append(to_chat_usernames)
            conditions.append(f"{chats_table_name}.username = ANY(${len(params)})")
        if from_user_ids:
            params.append(from_user_ids)
            conditions.append(f"from_user = ANY(${len(params)})")
        if from_user_usernames:
            params.append(from_user_usernames)
            conditions.append(f"{users_table_name}.username = ANY(${len(params)})")
        if has_text:
            conditions.append(
                f"{ForwardedMessage.__tablename__}.message_text IS NOT NULL"
            )

        conditions_str = " AND ".join(conditions) if conditions else ""

        return conditions_str, params
