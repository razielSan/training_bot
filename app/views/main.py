from aiogram import Router
from aiogram.types import (
    Message,
)
from aiogram.filters import CommandStart

from repositories.user import UserSQAlchemyRepository
from keyboards.reply_kb import get_menu_reply_kb
from extensions import bot


router = Router(name=__name__)


@router.message(CommandStart())
async def start(message: Message):
    """Реакция бот на нажатие /start."""
    name = message.from_user.first_name
    print(name, 1111)
    telegram = message.chat.id
    message_id = message.message_id - 1


    await bot.delete_message(chat_id=telegram, message_id=message_id)

    user = UserSQAlchemyRepository().get_user(telegram=telegram)
    if user:
        await message.answer(
            "Дневник тренировок",
            reply_markup=get_menu_reply_kb(),
        )
    else:
        user = UserSQAlchemyRepository().create_user(
            name=name,
            telegram=telegram,
        )
        if user:
            await message.answer(
                "Дневник тренировок",
                reply_markup=get_menu_reply_kb(),
            )
        else:
            await message.answer(
                "Произошла ошибка при регистрации. Попробуйте ввести еще раз /start"
            )
