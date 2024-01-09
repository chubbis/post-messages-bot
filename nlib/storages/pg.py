import asyncio

import asyncpg

from config import config

shared_event_loop = asyncio.get_event_loop()


class PoolConnection:
    def __init__(self, pool):
        self.pool = pool
        self.conn = None

    async def __aenter__(self):
        self.conn = await self.pool.acquire()
        # await self.conn.set_type_codec(
        #     "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
        # )
        # await self.conn.set_builtin_type_codec(
        #     "hstore", schema=config.PG_SCHEMA, codec_name="pg_contrib.hstore"
        # )
        # await self.conn.set_type_codec(
        #     "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
        # )
        return self.conn

    async def __aexit__(self, *_, **__):
        await self.pool.release(self.conn)


class AsyncDbManager:
    """
    Connection pool for async connections
    """

    def __init__(self, pg_dsn: str):
        self.pool = None
        self.dsn = pg_dsn

    async def __call__(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                command_timeout=60,
                loop=shared_event_loop,
                ssl=config.PGSSLMODE,
            )
        return PoolConnection(self.pool)


adb_session = AsyncDbManager(config.PG_DSN)
