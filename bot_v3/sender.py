from aiogram import types

from bot_v3.lib.bot import bot


class SendMessage:
    @classmethod
    async def send_answer(cls, message: types.Message, message_text: str):
        return await message.answer(message_text)

    @classmethod
    async def forward_message(
        cls, chat_id: int, from_chat_id: int, to_chat_message_id: int
    ):
        result = await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            to_chat_message_id=to_chat_message_id,
            protect_content=False,
        )

        return result

    @classmethod
    async def send_message(
        cls,
        chat_id: int,
        text: str,
        entities: list,
        disable_notification: bool = False,
        *_,
        **__
    ):
        result = await bot.send_message(
            chat_id=chat_id,
            text=text,
            entities=entities,
            disable_web_page_preview=True,
            disable_notification=disable_notification,
        )

        return result

    @classmethod
    async def send_photo(
        cls,
        chat_id: int,
        text: str,
        caption_entities: list,
        photo: str,
        disable_notification: bool = False,
        *_,
        **__
    ):
        result = await bot.send_photo(
            chat_id=chat_id,
            caption=text,
            caption_entities=caption_entities,
            photo=photo,
            disable_notification=disable_notification,
        )

        return result

    @classmethod
    async def send_document(
        cls,
        chat_id: int,
        text: str,
        caption_entities: list,
        document: str,
        disable_notification: bool = False,
        *_,
        **__
    ):
        result = await bot.send_document(
            chat_id=chat_id,
            caption=text,
            caption_entities=caption_entities,
            document=document,
            disable_notification=disable_notification,
        )

        return result

    @classmethod
    async def edit_sent_text_message(
        cls, message_id: int, text: str, chat_id: int, entities: list, *_, **__
    ):
        result = await bot.edit_message_text(
            text=text,
            message_id=message_id,
            chat_id=chat_id,
            entities=entities,
        )

        return result

    @classmethod
    async def edit_sent_caption_message(
        cls, message_id: int, text: str, chat_id: int, caption_entities: list, *_, **__
    ):
        result = await bot.edit_message_caption(
            caption=text,
            message_id=message_id,
            chat_id=chat_id,
            caption_entities=caption_entities,
        )

        return result

    @classmethod
    async def delete_message(cls, message_id: int, chat_id: int):
        result = await bot.delete_message(chat_id=chat_id, message_id=message_id)

        return result
