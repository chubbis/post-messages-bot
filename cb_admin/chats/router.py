from fastapi import APIRouter

from . import views
from .schemas import ChatFullOutput, ChatsOutput

router = APIRouter(prefix="/api", tags=["Chats"])

router.add_api_route(
    "/v1/chats/{chat_id}/",
    methods=["GET"],
    endpoint=views.get_chat_by_id,
    response_model=ChatFullOutput,
    status_code=200,
    responses={
        404: {"description": "Chat Not Found"},
    },
)

router.add_api_route(
    "/v1/chats/",
    methods=["GET"],
    endpoint=views.get_chats,
    response_model=ChatsOutput,
    status_code=200,
    responses={
        404: {"description": "Chat Not Found"},
    },
)
