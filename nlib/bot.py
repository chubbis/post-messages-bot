from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import config

# Initialize bot
bot = Bot(config.API_TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())
