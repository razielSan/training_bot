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
    name = message.from_user.username
    telegram = message.chat.id
    message_id = message.message_id - 1

    count = await bot.get_chat_member_count(telegram)
    await bot.delete_message(chat_id=telegram, message_id=message_id)

    if telegram not in bot.my_admins_list and count == 2:
        """Присваивание статуса администратора создателю бота при первом нажатии /start.""" 
        bot.my_admins_list.append(telegram)
        user = UserSQAlchemyRepository().create_user(
            name=name,
            telegram=telegram,
            status="admin",
        )
        await message.answer(
            "Дневник тренировок",
            reply_markup=get_menu_reply_kb(),
        )
    else:
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
