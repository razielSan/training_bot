from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from repositories.diary import DiarySQLAlchemyRepository
from repositories.user import UserSQAlchemyRepository
from models import Calendar, Diary

from config import settings


def get_buttons_add_a_workout():
    """Кнопки для выбора пользователем добавить ли еще тренировку."""
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="workout_+")],
            [InlineKeyboardButton(text="Нет", callback_data="workout_-")],
        ]
    )

    return inline_kb


def get_calendar_days(
    day_week: int,
    calendar: Calendar,
    telegram: int,
    button_back=True,
    button_forward=True,
):
    """Возвращает календарь c помечанным на нем тренировочными днями."""
    user = UserSQAlchemyRepository().get_user(telegram=telegram)

    list_days = DiarySQLAlchemyRepository().get_list_day_for_diary(
        year=calendar.year,
        month=calendar.month,
        user_id=user.id,
    )

    inline_keyboard = InlineKeyboardBuilder()

    for day in settings.day_week:
        inline_keyboard.button(text=day, callback_data=day)

    count = 0

    for i in range(0, day_week):
        inline_keyboard.button(text="*", callback_data=f"{i}")
        count += 1

    for day in range(1, calendar.count_days + 1):
        if not list_days:
            inline_keyboard.button(text=f"{day}", callback_data=f"{day}")
        else:
            if day in list_days:
                inline_keyboard.button(
                    text="💪",
                    callback_data=f"diary {calendar.year}.{calendar.month}.{day}",
                )
            else:
                inline_keyboard.button(text=f"{day}", callback_data=f"{day}")
        count += 1

    if count % 7:
        data = count % 7
        count = 7 - data
        for i in range(count):
            inline_keyboard.button(text="*", callback_data=f"{count}")

    inline_keyboard.adjust(7)

    button1 = InlineKeyboardButton(
        text="👈  Назад",
        callback_data=f"calendar - {calendar.year}.{calendar.month}",
    )
    button2 = InlineKeyboardButton(
        text="Вперед  👉",
        callback_data=f"calendar + {calendar.year}.{calendar.month}",
    )

    buttons_list = []
    if button_back:
        buttons_list.append(button1)
    if button_forward:
        buttons_list.append(button2)

    inline_keyboard.row(*buttons_list)

    return inline_keyboard.as_markup()


def get_buttons_by_diary(
    diary: Diary,
    completed: bool,
    back_button=True,
    forward_button=True,
):
    """Возвращает инлайн кнопки назад и вперед для дневника."""
    inline_kb = InlineKeyboardBuilder()

    if back_button:
        inline_kb.add(
            InlineKeyboardButton(
                text="👈  Назад",
                callback_data=f"diary - {diary.date.year}.{diary.date.month}.{diary.date.day}.{diary.date.hour}",
            )
        )

    if forward_button:
        inline_kb.add(
            InlineKeyboardButton(
                text="Вперед  👉",
                callback_data=f"diary + {diary.date.year}.{diary.date.month}.{diary.date.day}.{diary.date.hour}",
            )
        )
    if not completed:
        inline_kb.row(
            InlineKeyboardButton(
                text="Начать тренировку",
                callback_data=f"start_training {diary.training_count}.{diary.date.year}.{diary.date.month}.{diary.date.day}.{diary.date.hour}",
            ),
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text="Информация о тренировке",
                callback_data=f"info_training {diary.training_count}.{diary.date.year}.{diary.date.month}.{diary.date.day}.{diary.date.hour}",
            ),
        )

    inline_kb.row(
        InlineKeyboardButton(
            text="Удалить тренировку",
            callback_data=f"delete {diary.training_count}.{diary.date.year}.{diary.date.month}.{diary.date.day}.{diary.date.hour}",
        ),
    )

    # inline_kb.adjust(2, 1, 1)
    return inline_kb.as_markup()


def get_buttons_add_a_approach():
    """Кнопки для выбора пользователем добавить ли один повтор."""
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="approach_+")],
            [InlineKeyboardButton(text="Нет", callback_data="approach_-")],
        ]
    )

    return inline_kb
