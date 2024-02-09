import asyncio

from fastapi import Depends, HTTPException, Query

from cb_admin.chats.schemas import ChatsNextPageQuery, ChatsOutput
from cb_admin.common.dependencies import check_app_key
from models.chats.models import Chat


async def get_chat_by_id(
    chat_id: int,
    _: dict = Depends(check_app_key),
):
    chat = await Chat.get_chat_by_id(chat_id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return dict(chat)


async def get_chats(
    next_page: str = Query(None, description="Next page key"),
    limit: int = Query(10, description="Response Limit", ge=1, le=20),
    _: dict = Depends(check_app_key),
):
    if next_page:
        query_obj = ChatsNextPageQuery.from_str(next_page)
    else:
        query_obj = ChatsNextPageQuery(limit=limit, offset=0)

    chats, count = await asyncio.gather(
        Chat.get_chats(**dict(query_obj)),
        Chat.get_chats_count(),
    )
    chats = [dict(**chat) for chat in chats]
    next_page = None
    if len(chats) > limit:
        query_obj.offset += limit
        chats = chats[:limit]
        next_page = query_obj.as_str

    return ChatsOutput(groups=chats, next_page=next_page, count=count)
