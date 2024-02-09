import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request


def serialize_messages(request: "Request", messages: list) -> list[dict]:
    result = []
    for m in messages:
        message = dict(m)
        if isinstance(message["entities"], str):
            message["entities"] = json.loads(message["entities"])
        if not message["entities"]:
            message["entities"] = []

        if isinstance(message["from_chat"], str):
            message["from_chat"] = json.loads(message["from_chat"])

        if isinstance(message["to_chat"], str):
            message["to_chat"] = json.loads(message["to_chat"])

        if isinstance(message["from_user_info"], str):
            message["from_user_info"] = json.loads(message["from_user_info"])

        if message["file_ids"]:
            message["file_links"] = []
            for file_id in message["file_ids"]:
                message["file_links"].append(
                    str(
                        request.url_for(
                            "download_captures",
                            model_type=message["model_type"],
                            file_id=file_id,
                        )
                    )
                )

        result.append(message)

    return result
