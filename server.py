import logging

from aiogram import executor

from handlers import *
from middleware.serialize_message import SerializeMessageMiddleware
from nlib.bot import dp

logging.basicConfig(
    format="%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)

if __name__ == "__main__":
    dp.middleware.setup(SerializeMessageMiddleware())
    executor.start_polling(dp, skip_updates=True)
