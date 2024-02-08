from datetime import datetime

from pydantic import BaseModel

from common.base_schemas import ChatBase
from common.pagination import BasePageQuery


class ChatFullOutput(ChatBase):
    created_at: datetime
    updated_at: datetime


class ChatsOutput(BaseModel):
    groups: list[ChatFullOutput]
    next_page: str | None
    count: int | None


class ChatsNextPageQuery(BasePageQuery):
    limit: int
    offset: int
