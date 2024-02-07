import pytest

from models.messages.models import ForwardedMessage


@pytest.mark.asyncio
async def test_save_new_message():
    result = await ForwardedMessage.save_message(
        from_chat_id=pytest.from_chat_id,
        from_user=pytest.from_user_id,
        to_chat_id=pytest.to_chat_id,
        from_message_id=pytest.from_message_id_1,
        to_chat_message_id=pytest.to_chat_message_id_1,
        is_private=False,
        model_type="text",
        message_text="super important text",
        file_id=None,
        entities="",
    )
    assert result == 33333


@pytest.mark.asyncio
async def test_get_massage():
    result = await ForwardedMessage.get_message(
        from_message_id=pytest.from_message_id_1, from_chat_id=pytest.from_chat_id
    )
    assert result["to_chat_message_id"] == pytest.to_chat_message_id_1
    assert result["is_deleted"] is False


@pytest.mark.asyncio
async def test_get_no_exists_massage():
    result = await ForwardedMessage.get_message(
        from_message_id=-1, from_chat_id=pytest.from_chat_id
    )
    assert result == {}


@pytest.mark.asyncio
async def test_save_another_message():
    result = await ForwardedMessage.save_message(
        from_chat_id=pytest.from_chat_id,
        from_user=pytest.from_user_id,
        to_chat_id=pytest.to_chat_id,
        from_message_id=pytest.from_message_id_2,
        to_chat_message_id=pytest.to_chat_message_id_2,
        is_private=False,
        model_type="text",
    )
    assert result == pytest.to_chat_message_id_2


@pytest.mark.asyncio
async def test_get_massage_2():
    result = await ForwardedMessage.get_message(
        from_message_id=pytest.from_message_id_2, from_chat_id=pytest.from_chat_id
    )
    assert result["to_chat_message_id"] == pytest.to_chat_message_id_2
    assert result["is_deleted"] is False


@pytest.mark.asyncio
async def test_delete_exist_message():
    result = await ForwardedMessage.delete_with_message_id(
        from_message_id=pytest.from_message_id_2, from_chat_id=pytest.from_chat_id
    )
    assert result == pytest.to_chat_message_id_2


@pytest.mark.asyncio
async def test_delete_not_exist_message_id():
    result = await ForwardedMessage.delete_with_message_id(
        from_message_id=-1, from_chat_id=pytest.from_chat_id
    )
    assert result is None


@pytest.mark.asyncio
async def test_delete_not_exist_from_chat_id():
    result = await ForwardedMessage.delete_with_message_id(
        from_message_id=pytest.from_message_id_2, from_chat_id=-1
    )
    assert result is None
