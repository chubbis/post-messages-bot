from datetime import datetime

from pydantic import BaseModel

from common.base_schemas import ChatBase, UserBase
from common.pagination import BasePageQuery


class UserOutput(UserBase):
    id: int | None
    username: str | None = None
    link: str | None = None


class MessageBase(BaseModel):
    id: int
    from_chat: ChatBase | None = None
    from_user_info: UserOutput | None = None
    to_chat: ChatBase | None = None
    message_text: str | None = None
    file_link: str | None = None
    entities: list[dict] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MessagesOutput(BaseModel):
    messages: list[MessageBase]
    next_page: str | None = None
    count: int = 0


class MessagesNextPageQuery(BasePageQuery):
    from_chat_ids: list[int] | None = None
    from_chat_usernames: list[str] | None = None
    to_chat_ids: list[int] | None = None
    to_chat_usernames: list[str] | None = None
    from_user_ids: list[int] | None = None
    from_user_usernames: list[str] | None = None
    order_by: list[str] | None = None
    order_type_desc: bool = False
    has_text: bool = True
    limit: int = 10
    offset: int = 0
