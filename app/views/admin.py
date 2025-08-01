from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from keyboards.reply_kb import get_menu_admin, get_button_update_calendar
from repositories.user import UserSQAlchemyRepository
from repositories.calendar import CalendarSQLAlchemyRepository
from repositories.calendar import CalendarSQLAlchemyRepository
from repositories.calendardays import CalendarDaysSQLAlchemyRepository
from extensions import bot


from filters.admin import IsAdmin

router = Router(name=__name__)
router.message.filter(IsAdmin())


class AddCalendar(StatesGroup):
    year = State()
    month = State()
    count_days = State()

    text = {
        "AddCalendar:year": "Введите год",
        "AddCalendar:month": "Введите месяц",
        "AddCalendar:count_days": "Введите количество дней в месяце",
    }


@router.message(F.text == "/admin")
async def get_menu_for_admin(message: Message):
    """Возвращает меню администратора."""
    message_id = message.message_id - 1
    telegram = message.chat.id
    user = UserSQAlchemyRepository().get_user(telegram=telegram)

    await bot.delete_message(chat_id=telegram, message_id=message_id)

    await message.answer(
        "Выберите действие",
        reply_markup=get_menu_admin(),
    )


@router.message(StateFilter(None), F.text == "Заполнить календарь")
async def add_calendar(message: Message, state: FSMContext):
    """Реакция на кнопку 'Заполнить календарь' в FSM."""
    telegram = message.chat.id

    await message.answer(
        "Введите год",
        reply_markup=get_button_update_calendar(),
    )

    await state.set_state(AddCalendar.year)


@router.message(StateFilter("*"), F.text == "<Отмена>")
async def cancel_calendar_handler(message: Message, state: FSMContext):
    """Реакция бота на нажатие кнопки '<Отмена>' в календаре."""
    current_state = await state.get_state()

    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Действия отменены\n\nВыберите действие",
        reply_markup=get_menu_admin(),
    )


@router.message(StateFilter("*"), F.text == "<Назад>")
async def back_calendar_handler(message: Message, state: FSMContext):
    """Реакция бота на нажатие кнопки '<Назад>' в календаре."""
    current_state = await state.get_state()

    if current_state == AddCalendar.year:
        await message.answer("Предыдущего шага нет.\nВведите год или нажмите отмена")
        return

    previous = 0
    for step in AddCalendar.__all_states__:
        if current_state == step.state:
            await state.set_state(previous)
            await message.answer(
                f"Хорошо, вы вернулись к прошлому шагу\n\n{AddCalendar.text[previous.state]}",
            )
            return
        previous = step


@router.message(AddCalendar.year, F.text)
async def add_year(message: Message, state: FSMContext):
    """Реакция на действие 'Введите год'."""
    await state.update_data(year=message.text)

    await message.answer("Введите месяц")
    await state.set_state(AddCalendar.month)


@router.message(AddCalendar.month, F.text)
async def add_month(message: Message, state: FSMContext):
    """Реакция на действие 'Введите месяц'."""
    await state.update_data(month=message.text)

    await message.answer("Введите количество дней в месяце")
    await state.set_state(AddCalendar.count_days)


@router.message(AddCalendar.count_days, F.text)
async def add_count_days(message: Message, state: FSMContext):
    """Реакция на действие 'Введите количество дней в месяце.'"""
    data = await state.get_data()

    calendar, mess = CalendarSQLAlchemyRepository().add_calendar(
        year=data["year"],
        month=data["month"],
        count_days=message.text,
    )
    if calendar:
        calendar = CalendarSQLAlchemyRepository().get_calendar_by_date(
            year=int(data["year"]),
            month=int(data["month"]),
        )

        data = CalendarDaysSQLAlchemyRepository().add_calendar_days(
            count_day=calendar.count_days,
            calendar_id=calendar.id,
            year=int(data["year"]),
            month=int(data["month"]),
        )

        await state.clear()
        await message.answer(
            "Данные успешно добавлены\n\nВведите действие",
            reply_markup=get_menu_admin(),
        )
    else:
        await message.answer(
            f"{mess['error']}\n\nВведите год",
            reply_markup=get_button_update_calendar(),
        )
        await state.set_state(AddCalendar.year)
