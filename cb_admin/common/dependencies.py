import json

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose.exceptions import JWTError

from cb_admin.common.jwt_token import get_token_data

from models.users.models import UserToken


async def check_app_key(
        auth_bearer: str = Depends(
            APIKeyHeader(
                name="Authorization",
                description="access token",
            )
        )
):
    _, access_token = auth_bearer.split(" ")

    if not access_token:
        raise HTTPException(status_code=403)

    try:
        token_data = get_token_data(token=access_token)
    except JWTError:
        raise HTTPException(status_code=403)

    app_data = json.loads(token_data.get("sub"))
    user_token = await UserToken.get_token_by_user_id(user_id=app_data["id"])

    if not user_token and access_token != user_token:
        raise HTTPException(status_code=403)

    return app_data
