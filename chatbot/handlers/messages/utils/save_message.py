from models.messages.models import ForwardedMessage
from models.users.models import Users


def prepare_save_message_coros(
        from_chat_id: int,
        from_user: int,
        from_message_id: int,
        to_chat_id: int,
        is_private: bool,
        to_chat_message_id: int,
        model_type: str,
        entities: str,
        file_id: str | None,
        message_text: str,
        username: str,
):
    return [
        ForwardedMessage.save_message(
            from_chat_id=from_chat_id,
            from_user=from_user,
            from_message_id=from_message_id,
            to_chat_id=to_chat_id,
            is_private=is_private,
            to_chat_message_id=to_chat_message_id,
            model_type=model_type,
            entities=entities,
            file_id=file_id,
            message_text=message_text,
        ),
        Users.update_or_create_user(user_id=from_user, username=username),
    ]
