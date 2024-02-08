from enum import Enum


class ModelTypeEnum(Enum):
    text_message = "text"
    photo_message = "photo"
    document_message = "document"


class TextPath(Enum):
    text = "text"
    photo = "caption"
    document = "caption"


class EntitiesPath(Enum):
    text = "entities"
    photo = "caption_entities"
    document = "caption_entities"


class AvailableFilesModelType(Enum):
    photo = "photo"
    document = "document"


class ModelTypeExtensions(Enum):
    photo = "jpeg"
    document = "pdf"
