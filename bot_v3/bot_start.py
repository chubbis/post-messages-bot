from aiogram import Dispatcher

from bot_v3.handlers.messages.handlers import messages_router
from bot_v3.lib.bot import bot
from bot_v3.middlewares.serialize_message import SerializeMessageMiddleware

dp = Dispatcher()


# add middleware
messages_router.message.middleware(SerializeMessageMiddleware())
messages_router.edited_message.middleware(SerializeMessageMiddleware())

# register routers
dp.include_routers(messages_router)


async def start_chatbot():
    await dp.start_polling(bot)
