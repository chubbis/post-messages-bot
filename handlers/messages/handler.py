import logging

from aiogram import types

from handlers.messages.views import (
    process_delete_message,
    process_edited_message,
    process_new_message,
)
from nlib.bot import dp
from nlib.hashtags import hashtags_service

logger = logging.getLogger(__name__)


@dp.message_handler(
    hashtags_service.check,
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    content_types=["photo", "text", "document"],
)
async def process_new_message_handler(
    message: types.Message, model_type: str, message_text: str, file_id: str = None
):
    """
    Forward message with vacancy or cv
    :param message_text: text from 'text'(for model_type=='text') or 'caption'(for model_type=='photo')
    :param model_type: message type  'photo', 'text'
    :param message: aiogram Message object
    :param file_id: str - file id from tm to send in message
    :return:
    """
    await process_new_message(
        message=message,
        model_type=model_type,
        message_text=message_text,
        file_id=file_id,
        to_chat_id=hashtags_service.get_to_chat_id(message.chat.id),
    )


@dp.edited_message_handler(
    hashtags_service.check,
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    content_types=["photo", "text", "document"],
)
async def process_edited_message_handler(
    message: types.Message,
    model_type: str,
    message_text: str,
    file_id: str = None,
):
    """
    Forward message with vacancy or cv
    TODO add message obj example
    :param message_text: text from 'text'(for model_type=='text') or 'caption'(for model_type=='photo')
    :param model_type: message type  'photo', 'text'
    :param message: aiogram Message object
    :param file_id: str - file id from tm to send in message
    :return:
    """
    await process_edited_message(
        message=message,
        model_type=model_type,
        message_text=message_text,
        file_id=file_id,
        to_chat_id=hashtags_service.get_to_chat_id(message.chat.id),
    )


@dp.edited_message_handler(
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    content_types=["photo", "text", "document"],
)
async def process_delete_message_handler(
    message: types.Message,
):
    await process_delete_message(message=message)
