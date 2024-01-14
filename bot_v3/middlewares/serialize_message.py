import json
import typing
from enum import Enum
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

if typing.TYPE_CHECKING:
    from aiogram.types import Message


class ModelTypeEnum(Enum):
    text_message = "text"
    photo_message = "photo"
    document_message = "document"


class TextPath(Enum):
    text = "text"
    photo = "caption"
    document = "caption"


class EntitiesPath(Enum):
    text = "entities"
    photo = "caption_entities"
    document = "caption_entities"


class SerializeMessageMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: "Message",
        data: Dict[str, Any],
    ):
        model_type = self.__get_model_type(event)
        if not model_type:
            return

        data["model_type"] = model_type
        data["message_text"] = getattr(event, TextPath[model_type].value, "")
        data["entities"] = self.__get_entities(event, model_type)

        if model_type == "photo":
            data["file_id"] = event.photo[0].file_id
        if model_type == "document":
            if event.document.mime_type != "application/pdf":
                return
            data["file_id"] = event.document.file_id
        result = await handler(event, data)
        return result

    @staticmethod
    def __get_model_type(message: "Message") -> str | None:
        model_type = ""
        if message.photo:
            model_type = ModelTypeEnum.photo_message.value
        elif message.document:
            if message.document.mime_type == "application/pdf":
                model_type = ModelTypeEnum.document_message.value
        elif message.text:
            model_type = ModelTypeEnum.text_message.value

        return model_type

    @staticmethod
    def __get_entities(message: "Message", model_type: str) -> str:
        entities = getattr(message, EntitiesPath[model_type].value)
        if not entities:
            return ""
        return json.dumps([dict(entity) for entity in entities])
