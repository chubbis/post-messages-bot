import asyncio

from aiogram import types

from chatbot.handlers.messages.utils.add_author import add_author
from chatbot.handlers.messages.utils.check_message_min_length import (
    check_message_length,
)
from chatbot.handlers.messages.utils.save_message import prepare_save_message_coros
from chatbot.lib.sender import SendMessage
from common.enums import ModelTypeEnum
from models.messages.last_group_media_file_ids import LastGroupMediaFileIds
from models.messages.models import ForwardedMessage

SEND_MESSAGE_MAP = {
    "text": SendMessage.send_message,
    "photo": SendMessage.send_photo,
    "document": SendMessage.send_document,
    "media_group": SendMessage.send_media_group,
}
EDITED_MESSAGE_MAP = {
    "text": SendMessage.edit_sent_text_message,
    "photo": SendMessage.edit_sent_caption_message,
    "document": SendMessage.edit_sent_caption_message,
    "media_group": SendMessage.edit_sent_caption_message,
}


async def process_new_message(
    message: types.Message,
    model_type: str,
    message_text: str,
    to_chat_id: int,
    entities: str,
    file_ids: list[str] = None,
) -> int:
    need_forward = await check_message_length(
        from_chat_id=message.chat.id, message_text=message_text
    )
    if not need_forward:
        return 1

    text_with_author = add_author(
        text=message_text, author_name=message.from_user.username
    )
    params = {
        "text": text_with_author,
        "chat_id": to_chat_id,
        "entities": message.entities,
        "photo": file_ids[0]
        if model_type == ModelTypeEnum.photo_message.value
        else file_ids,
        "document": file_ids,
        "caption_entities": message.caption_entities,
    }
    result = await SEND_MESSAGE_MAP[model_type](**params)

    if not result:
        return 1

    is_private = message.chat.type == "private"
    coros = prepare_save_message_coros(
        from_chat_id=message.chat.id,
        from_user=message.from_user.id,
        from_message_id=message.message_id,
        to_chat_id=to_chat_id,
        is_private=is_private,
        to_chat_message_id=result.message_id,
        model_type=model_type,
        entities=entities,
        file_ids=file_ids,
        message_text=message_text,
        username=message.from_user.username,
    )
    await asyncio.gather(*coros)


async def process_edited_message(
    message: types.Message,
    model_type: str,
    message_text: str,
    to_chat_id: int,
    entities: str,
    file_ids: list[str] = None,
    **_
) -> int:
    result: dict = await ForwardedMessage.get_message(
        from_message_id=message.message_id,
        from_chat_id=message.chat.id,
    )
    if not result and model_type == ModelTypeEnum.media_group_message.value:
        file_ids = await LastGroupMediaFileIds.get_media_group_info(
            from_message_id=message.message_id,
            from_chat_id=message.chat.id,
        )
        if not file_ids:
            return 0

    if not result:
        await process_new_message(
            message=message,
            model_type=model_type,
            message_text=message_text,
            file_ids=file_ids,
            to_chat_id=to_chat_id,
            entities=entities,
        )
        return 0
    db_file_ids = result["file_ids"]
    editing_message_id: int = result["to_chat_message_id"]
    is_message_deleted: bool = result["is_deleted"]

    need_edit = await check_message_length(
        from_chat_id=message.chat.id, message_text=message_text
    )
    # if length after edited message less than GLOBAL_VARS - need to delete message from channel
    if not need_edit:
        await process_delete_message(message=message)
        return 0

    # check that message text have author and add if not
    new_text = add_author(text=message_text, author_name=message.from_user.username)
    params = {
        "message_id": editing_message_id,
        "text": new_text,
        "chat_id": to_chat_id,
        "entities": message.entities,
        "caption_entities": message.caption_entities,
        "disable_notification": is_message_deleted,
        "photo": db_file_ids[0]
        if model_type == ModelTypeEnum.photo_message.value
        else db_file_ids,
        "document": file_ids,
    }
    if is_message_deleted:
        updated_message = await SEND_MESSAGE_MAP[model_type](**params)
    elif to_chat_id != result["to_chat_id"]:
        await process_delete_message(message=message)
        updated_message = await SEND_MESSAGE_MAP[model_type](**params)
    else:
        updated_message = await EDITED_MESSAGE_MAP[model_type](**params)

    if not updated_message:
        return 1

    is_private = message.chat.type == "private"
    coros = prepare_save_message_coros(
        from_chat_id=message.chat.id,
        from_user=message.from_user.id,
        from_message_id=message.message_id,
        to_chat_id=to_chat_id,
        is_private=is_private,
        to_chat_message_id=updated_message.message_id,
        model_type=model_type,
        entities=entities,
        file_ids=db_file_ids,
        message_text=message_text,
        username=message.from_user.username,
    )

    await asyncio.gather(*coros)


async def process_delete_message(message: types.Message):
    message_dict: dict = await ForwardedMessage.get_message(
        from_message_id=message.message_id,
        from_chat_id=message.chat.id,
    )
    if not message_dict:
        return 1

    deleting_message_id = message_dict["to_chat_message_id"]
    to_chat_id = message_dict["to_chat_id"]
    result = await ForwardedMessage.delete_with_message_id(
        from_message_id=message.message_id, from_chat_id=message.chat.id
    )
    messages_to_delete_count = 1
    if message_dict["file_ids"]:
        messages_to_delete_count = len(message_dict["file_ids"])
    if result:
        await SendMessage.delete_message(
            message_id=deleting_message_id,
            chat_id=to_chat_id,
            messages_to_delete_count=messages_to_delete_count,
        )


async def process_save_media_group(
    from_chat_id: int, from_message_id: int, file_ids: list[str]
):
    await LastGroupMediaFileIds.create_new_message(
        from_chat_id=from_chat_id, from_message_id=from_message_id, file_ids=file_ids
    )
