from aiogram import Bot
from aiogram.enums import ParseMode

from config import config

bot = Bot(config.API_TOKEN_BOT, parse_mode=ParseMode.HTML)
