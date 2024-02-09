import asyncio
import typing
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

if typing.TYPE_CHECKING:
    from aiogram.types import Message


class MediaGroupMiddleware(BaseMiddleware):
    media_group_file_ids = dict()
    latency: float = 0.01

    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: "Message",
        data: Dict[str, Any],
    ):
        if not event.media_group_id:
            return await handler(event, data)
        if event.photo:
            try:
                self.media_group_file_ids[event.media_group_id].append(
                    event.photo[0].file_id
                )
                return
            except KeyError:
                self.media_group_file_ids[event.media_group_id] = [
                    event.photo[0].file_id
                ]
                await asyncio.sleep(self.latency)

            data["media_group_file_ids"] = self.media_group_file_ids.pop(
                event.media_group_id
            )
            return await handler(event, data)

        # not need to handle messages with another caption types
        return
