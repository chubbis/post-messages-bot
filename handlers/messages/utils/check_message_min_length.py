from models.chat_settings.models import ChatSettings


async def check_message_length(from_chat_id: int, message_text: str) -> bool:
    min_message_length = await ChatSettings.get(
        "min_forward_message_length",
        from_chat_id,
    )

    if not min_message_length:
        return False

    return len(message_text) > int(min_message_length)
