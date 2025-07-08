from aiogram import Bot, Dispatcher
from sqlalchemy.orm import DeclarativeBase

from config import settings


dp = Dispatcher()
bot = Bot(token=settings.TOKEN)
bot.my_admins_list = [1383179677]


class Base(DeclarativeBase):
    pass
