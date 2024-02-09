from aiogram import F, Router, types
from aiogram.enums import ChatType

from chatbot.handlers.messages.views import (
    process_delete_message,
    process_edited_message,
    process_new_message,
    process_save_media_group,
)
from chatbot.lib.hashtags import hashtags_service

messages_router = Router()


@messages_router.message(
    F.chat.type.in_({ChatType.SUPERGROUP, ChatType.GROUP}),
    hashtags_service,
    F.content_type.in_({"text", "photo", "document"}),
)
async def process_new_message_handler(
    message: types.Message,
    model_type: str,
    message_text: str,
    file_ids: list[str] = None,
    entities: str = "",
):
    """
    Forward message with vacancy or cv
    :param message_text: text from 'text'(for model_type=='text') or 'caption'(for model_type=='photo')
    :param model_type: message type  'photo', 'text'
    :param message: aiogram Message object
    :param file_ids: list[str] - file id from tm to send in message
    :param entities: str JSON hashtags position in text
    :return:
    """
    await process_new_message(
        message=message,
        model_type=model_type,
        message_text=message_text,
        file_ids=file_ids,
        to_chat_id=hashtags_service.get_to_chat_id(message.chat.id),
        entities=entities,
    )


@messages_router.edited_message(
    F.chat.type.in_({ChatType.SUPERGROUP, ChatType.GROUP}),
    hashtags_service,
    F.content_type.in_({"text", "photo", "document"}),
)
async def process_edited_message_handler(
    message: types.Message,
    model_type: str,
    message_text: str,
    file_ids: list[str] = None,
    entities: str = "",
):
    """
    Forward message with vacancy or cv
    TODO add message obj example
    :param message_text: text from 'text'(for model_type=='text') or 'caption'(for model_type=='photo')
    :param model_type: message type  'photo', 'text'
    :param message: aiogram Message object
    :param file_ids: list[str] - file id from tm to send in message
    :param entities: str JSON hashtags position in text
    :return:
    """
    await process_edited_message(
        message=message,
        model_type=model_type,
        message_text=message_text,
        file_ids=file_ids,
        to_chat_id=hashtags_service.get_to_chat_id(message.chat.id),
        entities=entities,
    )


@messages_router.edited_message(
    F.chat.type.in_({ChatType.SUPERGROUP, ChatType.GROUP}),
    F.content_type.in_({"text", "photo", "document"}),
)
async def process_delete_message_handler(
    message: types.Message,
):
    await process_delete_message(message=message)


@messages_router.message(
    F.chat.type.in_({ChatType.SUPERGROUP, ChatType.GROUP}),
    F.media_group_id,
)
async def process_save_media_group_handler(
    message: types.Message,
    file_ids: list[str] = None,
    *_,
    **__,
):
    await process_save_media_group(
        from_chat_id=message.chat.id,
        from_message_id=message.message_id,
        file_ids=file_ids,
    )
