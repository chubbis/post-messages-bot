from models.chats.models import ChatSettings


async def check_message_length(
    to_chat_id: int, message_text: str, default_message_len: int = 180
) -> bool:
    min_message_length = await ChatSettings.get(
        "min_forward_message_length",
        to_chat_id,
    )

    if not min_message_length:
        min_message_length = default_message_len

    return len(message_text) > int(min_message_length)
