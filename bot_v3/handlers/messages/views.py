from aiogram import types

from bot_v3.handlers.messages.utils.add_author import add_author
from bot_v3.handlers.messages.utils.check_message_min_length import check_message_length
from bot_v3.sender import SendMessage
from models.messages.models import ForwardedMessage

SEND_MESSAGE_MAP = {
    "text": SendMessage.send_message,
    "photo": SendMessage.send_photo,
    "document": SendMessage.send_document,
}
EDITED_MESSAGE_MAP = {
    "text": SendMessage.edit_sent_text_message,
    "photo": SendMessage.edit_sent_caption_message,
    "document": SendMessage.edit_sent_caption_message,
}


async def process_new_message(
    message: types.Message,
    model_type: str,
    message_text: str,
    to_chat_id: int,
    entities: str,
    file_id: str = None,
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
        "photo": file_id,
        "document": file_id,
        "caption_entities": message.caption_entities,
    }
    result = await SEND_MESSAGE_MAP[model_type](**params)
    if not result:
        return 1

    is_private = message.chat.type == "private"

    await ForwardedMessage.save_message(
        from_chat_id=message.chat.id,
        from_user=message.from_user.id,
        from_message_id=message.message_id,
        to_chat_id=to_chat_id,
        is_private=is_private,
        to_chat_message_id=result.message_id,
        model_type=model_type,
        entities=entities,
        file_id=file_id,
        message_text=message_text,
    )


async def process_edited_message(
    message: types.Message,
    model_type: str,
    message_text: str,
    to_chat_id: int,
    entities: str,
    file_id: str = None,
    **_
) -> int:
    result: dict = await ForwardedMessage.get_message(
        from_message_id=message.message_id,
        from_chat_id=message.chat.id,
    )
    if not result:
        await process_new_message(
            message=message,
            model_type=model_type,
            message_text=message_text,
            file_id=file_id,
            to_chat_id=to_chat_id,
            entities=entities,
        )
        return 0

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
        "photo": file_id,
        "document": file_id,
    }
    if is_message_deleted:
        result: types.Message = await SEND_MESSAGE_MAP[model_type](**params)
    elif to_chat_id != result["to_chat_id"]:
        await process_delete_message(message=message)
        result: types.Message = await SEND_MESSAGE_MAP[model_type](**params)
    else:
        result: types.Message = await EDITED_MESSAGE_MAP[model_type](**params)

    is_private = message.chat.type == "private"

    if not result:
        return 1

    await ForwardedMessage.save_message(
        from_chat_id=message.chat.id,
        from_user=message.from_user.id,
        from_message_id=message.message_id,
        to_chat_id=to_chat_id,
        to_chat_message_id=result.message_id,
        model_type=model_type,
        is_private=is_private,
        message_text=message_text,
        entities=entities,
        file_id=file_id,
    )


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
    if result:
        await SendMessage.delete_message(
            message_id=deleting_message_id, chat_id=to_chat_id
        )
