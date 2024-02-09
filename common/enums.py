from enum import Enum


class ModelTypeEnum(Enum):
    text_message = "text"
    photo_message = "photo"
    document_message = "document"
    media_group_message = "media_group"


class TextPath(Enum):
    text = "text"
    photo = "caption"
    document = "caption"
    media_group = "caption"


class EntitiesPath(Enum):
    text = "entities"
    photo = "caption_entities"
    document = "caption_entities"
    media_group = "caption_entities"


class AvailableFilesModelType(Enum):
    photo = "photo"
    document = "document"
    group_media = "photo"


class ModelTypeExtensions(Enum):
    photo = "jpeg"
    document = "pdf"
