from enum import Enum

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class ModelTypeEnum(Enum):
    text_message = "text"
    photo_message = "photo"
    document_message = "document"


class TextPath(Enum):
    text = "text"
    photo = "caption"
    document = "caption"


class SerializeMessageMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        self.__process_handler(message=message, data=data)

    async def on_process_edited_message(self, message: types.Message, data: dict):
        self.__process_handler(message=message, data=data)

    def __process_handler(self, message: types.Message, data: dict):
        model_type = self.__get_model_type(message)
        data["model_type"] = model_type
        data["message_text"] = message[TextPath[model_type].value]
        if model_type == "photo":
            data["files_id"] = message.photo[0].file_id
        if model_type == "document":
            if message.document.mime_type != "application/pdf":
                raise CancelHandler
            data["file_id"] = message.document.file_id

    @staticmethod
    def __get_model_type(message: types.Message) -> str:
        model_type = ""
        if message.photo:
            model_type = ModelTypeEnum.photo_message.value
        if message.document:
            if message.document.mime_type != "application/pdf":
                raise CancelHandler
            model_type = ModelTypeEnum.document_message.value
        if message.text:
            model_type = ModelTypeEnum.text_message.value

        return model_type
