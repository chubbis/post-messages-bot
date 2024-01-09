import asyncio
import logging

from aiogram import types
from aiogram.dispatcher.filters import HashTag
from aiogram.dispatcher.handler import CancelHandler

from models.hashtags.models import Hashtags

logger = logging.getLogger(__name__)


class HashTagService(HashTag):
    from_chat_id_hashtags: dict[dict[int:str]] | dict = None
    message_hashtags: list[str]

    def __init__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._set_hashtags())
        hashtags = self._prepare_hashtags_list()
        super().__init__(hashtags=hashtags, cashtags=[])

    async def check(self, message: types.Message):
        if message.caption:
            text = message.caption
            entities = message.caption_entities
        elif message.text:
            text = message.text
            entities = message.entities
        else:
            return False

        hashtags = self._get_tags(text, entities)
        if self.hashtags and set(hashtags) & set(self.hashtags):
            self.message_hashtags = list(set(hashtags))
            return {"hashtags": self.message_hashtags}

    def _get_tags(self, text, entities) -> list[str]:
        hashtags = []

        for entity in entities:
            if entity.type == types.MessageEntityType.HASHTAG:
                value: str = entity.get_text(text).lstrip("#").lower()
                hashtags.append(value)

        return hashtags

    async def _set_hashtags(self):
        self.from_chat_id_hashtags = await Hashtags.get_hashtags()

    def _prepare_hashtags_list(self) -> list[str]:
        return list(
            set(
                hashtag
                for from_chat_id in self.from_chat_id_hashtags.keys()
                for hashtag in self.from_chat_id_hashtags[from_chat_id]
            )
        )

    def _get_to_chat_id(self, from_chat_id: int, hashtag: str) -> int:
        return self.from_chat_id_hashtags.get(from_chat_id, {}).get(hashtag)

    def get_to_chat_id(self, from_chat_id: int) -> int:
        group_ids = set(
            self._get_to_chat_id(from_chat_id, hashtag)
            for hashtag in self.message_hashtags
            if hashtag in self.hashtags
        )
        if len(group_ids) == 1:
            return group_ids.pop()

        logger.info(
            "Can't handler this message. Hashtags have different groups. Hashtags: %s. From chat id: %s. To chat ids: %s",
            self.hashtags,
            from_chat_id,
            group_ids,
        )
        raise CancelHandler


hashtags_service = HashTagService()
