import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cb_admin.chats.router import router as chats_router
from cb_admin.messages.router import router as messages_router


class CBAdminServer:
    routes = (
        messages_router,
        chats_router,
    )
    __slots__ = (
        "app",
        "host",
        "port",
        "log_level",
        "reload",
        "workers",
        "mode",
        "doc_urls",
        "openapi_url",
        "loop",
    )

    def __init__(
            self,
            host: str = "0.0.0.0",
            port: int = 8000,
            log_level: str = "info",
            reload: bool = True,
            workers: int = 1,
            debug: bool = False,
            loop=None,
    ):
        self.host = host
        self.port = port
        self.log_level = log_level
        self.reload = reload
        self.workers = workers
        self.loop = loop
        self.app = FastAPI(
            docs_url="/api/docs/" if debug else None,
            openapi_url="/api/docs/openapi.json" if debug else None,
        )
        self._add_middlewares()
        self._add_routes()

    async def _start_server(self):
        config = uvicorn.Config(
            self.app, port=self.port, log_level=self.log_level, reload=self.reload
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def run(self):
        await self._start_server()

    async def __call__(self, *args, **kwargs):
        await self.run()

    def _add_middlewares(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET"],
            allow_headers=[
                "Access-Control-Allow-Headers",
                "Content-Type",
                "Authorization",
                "Access-Control-Allow-Origin",
            ],
        )

    def _add_routes(self):
        for route in self.routes:
            self.app.include_router(route)
