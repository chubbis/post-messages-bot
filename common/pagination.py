from fernet import Fernet
from pydantic import BaseModel

from config import config

fernet = Fernet(config.FERNET_NEXT_PAGE.encode())


class BasePageQuery(BaseModel):
    @classmethod
    def from_str(cls, text: str) -> "BasePageQuery":
        data = fernet.decrypt(text.encode())
        return cls.model_validate_json(data)

    @property
    def as_str(self) -> str:
        data = fernet.encrypt(
            self.model_dump_json(exclude_unset=True, exclude_none=True).encode()
        )
        return data.decode()

    def __str__(self) -> str:
        return self.as_str
