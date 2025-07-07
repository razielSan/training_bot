from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery

from extensions import bot
from repositories.diary import DiarySQLAlchemyRepository
from repositories.user import UserSQAlchemyRepository
from functions import get_training_info

router = Router(name=__name__)


@router.callback_query(F.data.startswith("info_training "))
async def info_training(call: CallbackQuery):
    """Информация о тренировке."""
    _, data = call.data.split(" ")
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    training_count, year, month, day, hour = data.split(".")

    dtime = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour))
    user = UserSQAlchemyRepository().get_user(telegram=chat_id)
    diary_list = DiarySQLAlchemyRepository().get_diary(
        date=dtime, user_id=user.id, training_count=int(training_count)
    )
    data = get_training_info(list_diary=diary_list, user_id=user.id)

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.send_message(chat_id=chat_id, text=data)
