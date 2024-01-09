import asyncio

import pytest
from alembic import command
from alembic import config as alembic_config

from config import config

shared_event_loop = asyncio.get_event_loop()


def pytest_sessionstart(session):
    set_global_variables()


@pytest.fixture(scope="session")
async def setup_db():
    from nlib.storages.pg import AsyncDbManager

    # checkout to default postgres DB to terminate test DB's possible connections
    pg_base_local_pool = AsyncDbManager(config.PG_POSTGRES_DSN)
    async with await pg_base_local_pool() as conn:
        await conn.execute(
            """
            SELECT
                pg_terminate_backend(pg_stat_activity.pid)
            FROM
                pg_stat_activity
            WHERE
                pg_stat_activity.datname = 'test_montebot' AND
            pid <> pg_backend_pid();
        """
        )
        await conn.execute("DROP DATABASE IF EXISTS test_montebot;")
        await conn.execute("CREATE DATABASE test_montebot;")
    # checkout to test DB t
    local_pool = AsyncDbManager(config.PG_DSN)
    assert config.MODE == "test"
    alembic_conf = alembic_config.Config("alembic.ini")
    alembic_conf.set_section_option("alembic", "sqlalchemy.url", config.PG_DSN)

    print(" Upgrading database ", config.PG_DSN)
    command.upgrade(alembic_conf, "head")
    print(" Upgrading database ", config.PG_DSN, "finish")

    async with await local_pool() as conn:
        await conn.execute("DELETE FROM chat_settings")
        await conn.execute(
            """
            INSERT into chat_settings (variable_name, value, chat_id, user_id)
            VALUES ('min_forward_message_length', '20', '-1234', '-1')
        """
        )
        await conn.execute("DELETE FROM forwarded_messages")
    async with await local_pool() as conn:
        await conn.execute("DELETE FROM hashtag")
        await conn.execute(
            f"""
            INSERT into hashtag (from_chat_id, to_chat_id, hashtag_name)
            VALUES ({pytest.from_chat_id}, {pytest.to_chat_id}, 'vacancy')
        """
        )
    return


def set_global_variables():
    pytest.from_message_id_1 = 11111
    pytest.from_message_id_2 = 22222
    pytest.from_chat_id = -1234
    pytest.from_user_id = 11111
    pytest.to_chat_id = -4321
    pytest.to_chat_message_id_1 = 33333
    pytest.to_chat_message_id_2 = 44444


@pytest.fixture(scope="session")
def event_loop():
    return shared_event_loop
