from pydantic import BaseModel, model_validator


class ChatBase(BaseModel):
    id: int
    title: str | None = None
    username: str | None = None
    link: str | None = None
    chat_type: str | None = None

    @model_validator(mode="before")
    def prepare_link(cls, data):
        if data["username"]:
            data["link"] = f"https://t.me/{data['username']}"
        return data


class UserBase(BaseModel):
    id: int | None
    username: str | None = None
