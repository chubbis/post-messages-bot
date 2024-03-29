import json
import typing
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from common.enums import EntitiesPath, ModelTypeEnum, TextPath

if typing.TYPE_CHECKING:
    from aiogram.types import Message


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

        if model_type == ModelTypeEnum.photo_message.value:
            data["file_ids"] = [event.photo[0].file_id]
        if model_type == ModelTypeEnum.document_message.value:
            data["file_ids"] = [event.document.file_id]
        if model_type == ModelTypeEnum.media_group_message.value:
            data["file_ids"] = data.get("media_group_file_ids")
        result = await handler(event, data)
        return result

    @staticmethod
    def __get_model_type(message: "Message") -> str | None:
        model_type = ""
        if message.media_group_id and message.photo:
            model_type = ModelTypeEnum.media_group_message.value
        elif message.photo:
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
