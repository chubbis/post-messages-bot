import json

from jose import JWTError, jws, jwt
from pydantic import BaseModel

from config import config

ACCESS_KEY = config.JWT_TOKEN_ACCESS_KEY
ALGORITHM = config.JWT_TOKEN_ALGORITHM


class TokenInfo(BaseModel):
    access_token: str
    token: str = "bearer"
    expires: int = 0


class JWTTokenSchema(BaseModel):
    token: TokenInfo


def get_token_data(token: str) -> dict:
    try:
        data_obj = jwt.decode(token=token, key=ACCESS_KEY, algorithms=ALGORITHM)
    except JWTError:
        raise JWTError

    return data_obj


def create_access_token():
    """
    This func create access token.
    Before run fill token data with that you need
    Please run it from server.py.
    ex. python3 server.py -s create-access-token
    :return: None
    """
    token_data = {"add_your_data": "here"}
    access_token = jwt.encode(
        {"sub": json.dumps(token_data)}, key=ACCESS_KEY, algorithm=ALGORITHM
    )
    print(access_token)
