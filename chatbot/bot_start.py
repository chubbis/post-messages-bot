from aiogram import Dispatcher

from chatbot.handlers.messages.handlers import messages_router
from chatbot.middlewares.serialize_message import SerializeMessageMiddleware
from common.lib.bot import bot

dp = Dispatcher()


# add middleware
messages_router.message.middleware(SerializeMessageMiddleware())
messages_router.edited_message.middleware(SerializeMessageMiddleware())

# register routers
dp.include_routers(messages_router)


async def start_chatbot(loop=None):
    await dp.start_polling(bot, loop=loop)
