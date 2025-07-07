from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode

from extensions import bot
from keyboards.inline_kb import get_calendar_days
from repositories.calendar import CalendarSQLAlchemyRepository

router = Router(name=__name__)


@router.message(F.text == "Календарь тренировок")
async def get_calendar_training(message: Message):
    """Возвращает календарь тренировок пользователю."""
    telegram = message.chat.id

    mess = message.message_id - 1
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=mess,
    )

    date = datetime.now()
    calendar = CalendarSQLAlchemyRepository().get_calendar_by_date(
        year=date.year,
        month=date.month,
    )

    if calendar:
        day_week = datetime(calendar.year, calendar.month, 1).weekday()

        split_left = " " * 10
        split_right = " " * 10

        await message.answer(
            f"Календарь тренировок\n<b>{split_left}{calendar.month_name.capitalize()} {calendar.year}{split_right}</b>",
            reply_markup=get_calendar_days(
                day_week=day_week,
                calendar=calendar,
                telegram=telegram,
            ),
            parse_mode=ParseMode.HTML,
        ),
    else:
        await message.answer("Календарь еще не создан")

@router.callback_query(F.data.startswith("calendar "))
async def button_for_calendar(call: CallbackQuery):
    """Реакция на нажатие вперед или назад в календаре тренировок."""
    _, flag, data = call.data.split(" ")
    year, month = data.split(".")
    calendaries = CalendarSQLAlchemyRepository().get_calendars_by_filters(
        year=int(year),
        month=int(month),
        flag=flag,
    )

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    split_left = " " * 10
    split_right = " " * 10
    if len(calendaries) > 1:
        calendar = calendaries[0] if flag == "+" else calendaries[-1]
        day_week = datetime(calendar.year, calendar.month, 1).weekday()
        await bot.edit_message_text(
            text=f"Календарь тренировок\n<b>{split_left}{calendar.month_name.capitalize()} {calendar.year}{split_right}</b>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=get_calendar_days(
                day_week=day_week,
                calendar=calendar,
                telegram=chat_id,
            ),
            parse_mode=ParseMode.HTML,
        )
    else:
        button_back = True
        button_forward = True
        if flag == "+":
            button_forward = False
        elif flag == "-":
            button_back = False
        
        calendar = calendaries[0]
        day_week = datetime(calendar.year, calendar.month, 1).weekday()

        data = {
            "day_week": day_week,
            "calendar": calendar,
            "button_back": button_back,
            "button_forward": button_forward,
            "telegram": chat_id,
        }
        await bot.edit_message_text(
            text=f"Календарь тренировок\n<b>{split_left}{calendar.month_name.capitalize()} {calendar.year}{split_right}</b>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=get_calendar_days(
              **data,
            ),
            parse_mode=ParseMode.HTML,
        )
