import asyncio

from aiogram.exceptions import TelegramBadRequest
from fastapi import Depends, HTTPException, Request, status
from fastapi.params import Query
from fastapi.responses import StreamingResponse

from cb_admin.common.dependencies import check_app_key
from cb_admin.messages.schemas import MessageBase, MessagesNextPageQuery, MessagesOutput
from cb_admin.messages.serializes import serialize_messages
from common.enums import AvailableFilesModelType, ModelTypeExtensions
from common.lib.bot import bot
from models.messages.models import ForwardedMessage


async def get_message(
    message_id: int,
) -> MessageBase:
    message = await ForwardedMessage.get_message_by_id(message_id=message_id)
    return MessageBase(**message)


async def get_messages(
    request: Request,
    next_page: str = Query(None, description="Next page token"),
    from_chat_ids: list[int] = Query(
        None, description="List of chat ids, where message was posted"
    ),
    from_chat_usernames: list[str] = Query(
        None, description="List of chat usernames, where message was posted"
    ),
    to_chat_ids: list[int] = Query(
        None, description="List of chat ids where message was forwarded"
    ),
    to_chat_usernames: list[str] = Query(
        None, description="List of chat usernames where message was forwarded"
    ),
    from_user_ids: list[int] = Query(
        None, description="List of user ids, who posted this message"
    ),
    from_user_usernames: list[str] = Query(
        None, description="List of user usernames, who posted this message"
    ),
    has_text: bool = Query(
        True, description="Messages, there message text is not null (historical)"
    ),
    order_by: list[str] = Query(
        [f"{ForwardedMessage.__tablename__}.id"], description="Fields to order by"
    ),
    order_type_desc: bool = Query(False, description="Sorting direction"),
    limit: int = Query(10, ge=1, le=20, description="Records limit"),
) -> MessagesOutput:
    if next_page:
        query_obj = MessagesNextPageQuery.from_str(next_page)
    else:
        query_obj = MessagesNextPageQuery(
            from_chat_ids=from_chat_ids,
            from_chat_usernames=from_chat_usernames,
            to_chat_ids=to_chat_ids,
            to_chat_usernames=to_chat_usernames,
            from_user_ids=from_user_ids,
            from_user_usernames=from_user_usernames,
            order_by=order_by,
            order_type_desc=order_type_desc,
            has_text=has_text,
            limit=limit,
            offset=0,
        )
    messages, count_record = await asyncio.gather(
        ForwardedMessage.get_messages(**dict(query_obj)),
        ForwardedMessage.get_messages(only_count=True, **dict(query_obj)),
    )
    count = count_record[0]["count"]

    next_page = None
    if len(messages) > limit:
        query_obj.offset += limit
        messages = messages[:limit]
        next_page = query_obj.as_str

    return MessagesOutput(
        messages=serialize_messages(request, messages), next_page=next_page, count=count
    )


async def download_file(
    file_id: str,
    model_type: AvailableFilesModelType,
) -> StreamingResponse:
    try:
        file = await bot.get_file(file_id=file_id)
    except TelegramBadRequest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    content = await bot.download_file(file.file_path)
    return StreamingResponse(
        content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_id}.{ModelTypeExtensions[model_type.value].value}"
        },
    )
