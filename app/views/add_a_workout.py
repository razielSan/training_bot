from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from extensions import bot
from repositories.user import UserSQAlchemyRepository
from repositories.diary import DiarySQLAlchemyRepository
from repositories.calendardays import CalendarDaysSQLAlchemyRepository
from keyboards.inline_kb import get_buttons_add_a_workout
from keyboards.reply_kb import get_button_add_a_workout, get_menu_reply_kb
from functions import get_datetime_by_format, check_hour, chek_rest
from views.main import start
from config import settings


router = Router(name=__name__)


# Машина состояний для добавления тренировки в model Diary


class AddWorkout(StatesGroup):
    exersise = State()
    rest = State()
    date = State()
    hour = State()
    texts = {
        "AddWorkout:exersise": "Введите название упражнения",
        "AddWorkout:rest": "Введите необходимое время отдыха между подходами в минутах",
        "AddWorkout:date": "Введите дату начала тренировки в формате\n\nГод.Месяц.День",
    }


# Логика машины состояний для добавления тренировки в model Diary


@router.message(StateFilter(None), F.text == "Добавить тренировку")
async def add_exersise(message: Message, state: FSMContext):
    """Реакция бота на нажатие кнопки Добавить тренировку в FSM."""
    mess = message.message_id - 1

    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=mess,
    )

    await message.answer(
        "Введите название упражнения", reply_markup=get_button_add_a_workout()
    )

    await state.set_state(AddWorkout.exersise)


@router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state=FSMContext):
    """Реакция бота на нажатие кнопки отмена в FSM."""
    current_state = await state.get_state()
    if current_state is None:
        return

    settings.hour = 0
    settings.date_trainer = ""
    settings.plus_exercise = False
    settings.exercise_count = 0
    settings.new_training = True
    await state.clear()
    await message.answer(
        "Действия отменены\n\nДневник тренировок", reply_markup=get_menu_reply_kb()
    )


@router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_handler(message: Message, state=FSMContext):
    """Реакция бота на нажатие кнопки назад в FSM."""
    current_state = await state.get_state()

    if current_state == AddWorkout.exersise:
        await message.answer(
            "Предыдушего шага нет.\n\nВведите название упражнения или нажмите отмена "
        )
        return
    previous = None
    for step in AddWorkout.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Хорошо, вы вернулись к прошлому шагу\n\n{AddWorkout.texts[previous.state]}"
            )
            return

        previous = step


@router.message(AddWorkout.exersise, F.text)
async def add_rest(message: Message, state: FSMContext):
    """Реакция бота на введения пользователем упражнения в FSM."""
    await state.update_data(exersise=message.text)
    await message.answer("Введите необходимое время отдыха между подходами в минутах")

    await state.set_state(AddWorkout.rest)


@router.message(AddWorkout.date, F.text)
async def add_data(message: Message, state: FSMContext):
    """Реакция бота на введения пользователем даты и времени в FSM."""
    chat_id = message.chat.id

    date_trainer = message.text.split("\n")[-1]
    settings.date_trainer = date_trainer

    dtime, mess = get_datetime_by_format(date_trainer)
    if not dtime:
        await message.answer(mess["error"])
        await bot.send_message(
            chat_id=chat_id,
            text="Введите дату начала тренировки в формате\n\nГод.Месяц.День",
        )
        await state.set_state(AddWorkout.date)
    else:
        await state.update_data(date=message.text)

        await message.answer("Введите час начала тренировки")

        await state.set_state(AddWorkout.hour)


@router.message(AddWorkout.hour, F.text)
async def add_hour(message: Message, state: FSMContext):
    """Реакция бота на введения пользователем часа FSM."""
    telegram = message.chat.id
    user = UserSQAlchemyRepository().get_user(telegram=telegram)
    date_time, mess = get_datetime_by_format(settings.date_trainer)

    if not settings.hour:
        hour, mess = check_hour(message.text)
        if not hour:
            await message.answer(f"{mess['error']}\n\nВведите час начала тренировки")
            return

        # Проверка дневника чтобы не совпадал час начала тренировки
        diaries = DiarySQLAlchemyRepository().get_diary_by_date(
            user_id=user.id,
            date=datetime(
                year=date_time.year,
                month=date_time.month,
                day=date_time.day,
                hour=hour,
            ),
        )
        for diary in diaries:
            if diary.date.hour == hour:
                await message.answer(
                    "В этом часу уже есть тренировка\n\nВведите час начала тренировки"
                )
                return

        settings.hour = hour

    dtime = datetime(
        year=date_time.year,
        month=date_time.month,
        day=date_time.day,
        hour=settings.hour,
    )

    data = await state.get_data()
    exersise = data["exersise"]
    rest = float(data["rest"])

    settings.exercise_count += 1

    # Логика для вычисления какая по счету тренировка в день
    if settings.new_training:
        diaries_list = DiarySQLAlchemyRepository().get_diary_by_date(
            user_id=user.id,
            date=dtime,
            training_count=True,
        )
        if diaries_list:
            diary = diaries_list[-1]
            count = diary.training_count + 1
            settings.count = count
        else:
            settings.count = 1

    calendardays = CalendarDaysSQLAlchemyRepository().get_calendar_days(
        date=datetime(
            year=date_time.year,
            month=date_time.month,
            day=date_time.day,
        )
    )

    diary = await DiarySQLAlchemyRepository().create_diairy(
        user_id=user.id,
        exercise=exersise,
        rest=rest,
        date=dtime,
        exercise_count=settings.exercise_count,
        training_count=settings.count,
        calendardays_id=calendardays.id,
    )

    await bot.send_message(
        chat_id=telegram,
        text="Упражнение успешно записано. Желаете ли вы еще добавить упражнение в тренировку ?",
        reply_markup=get_buttons_add_a_workout(),
    )


@router.message(AddWorkout.rest, F.text)
async def add_datetime(message: Message, state: FSMContext):
    """Реакция бота на введения пользователем время отдыха в FSM."""
    chat_id = message.chat.id

    rest, mess = chek_rest(message.text)
    if not rest:
        await state.set_state(AddWorkout.rest)
        await message.answer(f"{mess['error']}")
        await bot.send_message(
            chat_id=chat_id,
            text="Введите необходимое время отдыха между подходами в минутах",
        )
    else:
        if settings.plus_exercise:
            await state.update_data(rest=message.text)
            await state.set_state(AddWorkout.hour)
            await add_hour(message, state)
        else:
            await state.update_data(rest=message.text)
            await bot.send_message(
                chat_id=chat_id,
                text="Введите дату начала тренировки в формате\n\nГод.Месяц.День",
            )

            await state.set_state(AddWorkout.date)


@router.callback_query(AddWorkout.hour, F.data.startswith("workout_"))
async def add_training(call: CallbackQuery, state: FSMContext):
    """Реакция бота на выбор добавления еще одного упражнения в FSM."""
    _, value = call.data.split("_")

    await state.clear()
    await call.message.edit_reply_markup()
    if value == "+":
        settings.new_training = False
        settings.plus_exercise = True
        await add_exersise(call.message, state)
    else:
        settings.hour = 0
        settings.date_trainer = ""
        settings.plus_exercise = False
        settings.new_training = True
        settings.exercise_count = 0
        await start(call.message)
