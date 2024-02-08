from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from . import views
from .schemas import MessageBase, MessagesOutput

router = APIRouter(prefix="/api", tags=["Messages"])

router.add_api_route(
    "/v1/message/{message_id}/",
    methods=["GET"],
    endpoint=views.get_message,
    response_model=MessageBase,
    status_code=200,
    responses={
        404: {"description": "Message Not Found"},
    },
)

router.add_api_route(
    "/v1/messages/",
    methods=["GET"],
    endpoint=views.get_messages,
    response_model=MessagesOutput,
    status_code=200,
    responses={
        404: {"description": "Message Not Found"},
    },
)

router.add_api_route(
    "/v1/message/file/{model_type}/{file_id}/",
    name="download_captures",
    methods=["GET"],
    endpoint=views.download_file,
    response_class=StreamingResponse,
    status_code=200,
    responses={
        404: {"description": "No file with such model_type and file_id"},
    },
)
