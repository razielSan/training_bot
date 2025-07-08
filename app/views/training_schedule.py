from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from repositories.diary import DiarySQLAlchemyRepository
from repositories.user import UserSQAlchemyRepository
from repositories.exercise import ExerciesSQLAlchemyRepository
from functions import get_training_data
from keyboards.inline_kb import get_buttons_by_diary
from extensions import bot


router = Router(name=__name__)


@router.message(F.text == "Расписание тренировок")
async def training_schedule(message: Message):
    """Расписание тренировок."""
    mess = message.message_id - 1

    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=mess,
    )

    telegram = message.chat.id
    user = UserSQAlchemyRepository().get_user(telegram=telegram)

    list_diary = DiarySQLAlchemyRepository().get_diary_list_all(user_id=user.id)

    if list_diary:
        data_training, completed = get_training_data(
            list_diary,
            user_id=user.id,
        )
        data = list_diary[0].date
        forward_button = DiarySQLAlchemyRepository().get_list_diaries_by_date(
            year=int(data.year),
            month=int(data.month),
            day=int(data.day),
            hour=data.hour,
            flag="+",
            user_id=user.id,
        )
        await message.answer(
            data_training,
            reply_markup=get_buttons_by_diary(
                list_diary[0],
                back_button=False,
                forward_button=forward_button,
                completed=completed,
            ),
        )
    else:
        await message.answer("В дневнике нет записей тренировок")


@router.callback_query(F.data.startswith("diary "))
async def get_button_for_diary(call: CallbackQuery):
    """Реакция на нажатие вперед или назад в расписание тренировок."""
    telegram = call.message.chat.id
    user = UserSQAlchemyRepository().get_user(telegram=telegram)

    message_id = call.message.message_id
    chat_id = call.message.chat.id

    data = call.data.split(" ")

    if len(data) == 2:
        mess = call.message.message_id

        await bot.delete_message(
            chat_id=chat_id,
            message_id=mess,
        )

        year, month, day = data[1].split(".")
        dtime = datetime(int(year), int(month), int(day))
        diary = DiarySQLAlchemyRepository().get_diary_by_date(
            user_id=user.id,
            date=dtime,
        )
        back_button = DiarySQLAlchemyRepository().get_list_diaries_by_date(
            year=diary[0].date.year,
            month=diary[0].date.month,
            day=diary[0].date.day,
            hour=diary[0].date.hour,
            flag="-",
            user_id=user.id,
        )
        forward_button = DiarySQLAlchemyRepository().get_list_diaries_by_date(
            year=int(year),
            month=int(month),
            day=int(day),
            hour=diary[0].date.hour,
            flag="+",
            user_id=user.id,
        )
        data_training, completed = get_training_data(
            diary,
            user_id=user.id,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=data_training,
            reply_markup=get_buttons_by_diary(
                diary[0],
                back_button=bool(back_button),
                forward_button=bool(forward_button),
                completed=completed,
            ),
        )

    else:
        _, flag, data = call.data.split(" ")
        year, month, day, hour = data.split(".")

        diaries = DiarySQLAlchemyRepository().get_list_diaries_by_date(
            year=int(year),
            month=int(month),
            day=int(day),
            hour=int(hour),
            user_id=user.id,
            flag=flag,
        )

        # Логика для вычисления количества тренировок по листу из тренировок
        diaries_count = 0
        data = None
        for index, diary in enumerate(diaries):
            if index == 0:
                diaries_count += 1
                data = diary
            else:
                if (
                    data.date == diary.date
                    and data.training_count == diary.training_count
                ):
                    pass
                else:
                    diaries_count += 1
                    data = diary

        data_training, completed = get_training_data(diaries, user_id=user.id)

        if diaries_count > 1:
            await bot.edit_message_text(
                text=data_training,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=get_buttons_by_diary(
                    diaries[0],
                    completed=completed,
                ),
            )
        else:
            back_button = False if flag == "-" else True
            forward_button = False if flag == "+" else True
            await bot.edit_message_text(
                text=data_training,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=get_buttons_by_diary(
                    diaries[0],
                    back_button=back_button,
                    forward_button=forward_button,
                    completed=completed,
                ),
            )


@router.callback_query(F.data.startswith("delete "))
async def delete_training(call: CallbackQuery):
    """Удаление тренировки."""
    telegram = call.message.chat.id
    message_id = call.message.message_id
    user = UserSQAlchemyRepository().get_user(telegram=telegram)
    data = call.data.split(" ")[-1]
    training_count, year, month, day, hour = data.split(".")


    diary, mess = DiarySQLAlchemyRepository().delete_diary(
        user_id=user.id,
        training_count=int(training_count),
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
    )
    
    if diary:
        await bot.delete_message(
            chat_id=telegram,
            message_id=message_id,
        )
        await bot.send_message(chat_id=telegram, text="Запись успешно удалена")

    else:
        await call.message.answer(mess["error"])
