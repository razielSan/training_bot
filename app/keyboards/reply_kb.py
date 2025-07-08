from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_menu_reply_kb():
    """Кнопки меню бота."""
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить тренировку"),
            ],
            [
                KeyboardButton(text="Расписание тренировок"),
            ],
            [
                KeyboardButton(text="Календарь тренировок"),
            ],
        ],
        resize_keyboard=True,
    )

    return reply_kb


def get_button_add_a_workout():
    """Кнопки для FSM добавления тренировки."""
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Назад"),
            ],
            [KeyboardButton(text="Отмена")],
        ]
    )
    return reply_kb


def get_menu_admin():
    """Возвращает меню для админа."""
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Заполнить календарь"),
            ],
        ],
    )
    return reply_kb


def get_button_update_calendar():
    """Кнопки для FSM заполения календаря."""
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="<Назад>"),
            ],
            [KeyboardButton(text="<Отмена>")],
        ]
    )
    return reply_kb


def get_button_by_exercies(rest=False,):
    """Кнопки для FSM заполнения упражнения."""
    reply_kb = ReplyKeyboardBuilder()
    if rest:
        reply_kb.add(KeyboardButton(text="пропустить отдых"))
    reply_kb.row(KeyboardButton(text="<<Отменa>>"))

    return reply_kb.as_markup()
