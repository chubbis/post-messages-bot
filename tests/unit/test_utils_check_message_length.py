import pytest

from handlers.messages.utils.check_message_min_length import check_message_length


@pytest.mark.asyncio
async def test_check_min_length_less_min_value():
    message_text = "Less than 20 chars"
    assert len(message_text) < 20
    need_edit = await check_message_length(
        from_chat_id=-1234, message_text=message_text
    )
    assert need_edit is False


@pytest.mark.asyncio
async def test_check_min_length_eq_min_value():
    message_text = "Eq. 20 characters..."
    assert len(message_text) == 20
    need_edit = await check_message_length(
        from_chat_id=-1234, message_text=message_text
    )
    assert need_edit is False


@pytest.mark.asyncio
async def test_check_min_length_more_min_value():
    message_text = "Less than 20 characters"
    assert len(message_text) > 20
    need_edit = await check_message_length(
        from_chat_id=-1234, message_text=message_text
    )
    assert need_edit is True
