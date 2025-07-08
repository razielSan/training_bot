import time
from datetime import datetime

from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from repositories.diary import DiarySQLAlchemyRepository
from repositories.user import UserSQAlchemyRepository
from repositories.exercise import ExerciesSQLAlchemyRepository
from extensions import bot
from config import settings
from functions import chek_data_by_int, removes_the_last_zeros
from keyboards.inline_kb import get_buttons_add_a_approach
from keyboards.reply_kb import get_button_by_exercies, get_menu_reply_kb


router = Router(name=__name__)


class AddExercise(StatesGroup):
    """FSM для упражнения."""
    exercise = State()
    approach = State()
    diary_id = State()
    repetition = State()
    count_exercise = State()
    rest = State()
    start_time = State()
    end_time = State()


@router.callback_query(StateFilter(None), F.data.startswith("start_training "))
@router.callback_query(AddExercise.end_time, F.data == "approach_-")
async def start_training(call: CallbackQuery, state: FSMContext):
    """Начало тренировки."""
    telegram = call.message.chat.id
    message_id = call.message.message_id

    await bot.delete_message(chat_id=telegram, message_id=message_id)
    if settings.start_exercise:
        settings.start_exercise = False
        training_count, year, month, day, hour = call.data.split(" ")[-1].split(".")

        dtime = datetime(int(year), int(month), int(day), int(hour))
        user = UserSQAlchemyRepository().get_user(telegram=telegram)
        diary_list = DiarySQLAlchemyRepository().get_diary(
            date=dtime,
            user_id=user.id,
            training_count=training_count,
        )
        diary = diary_list.pop(0)
        settings.exercise_list = diary_list
        await state.set_state(AddExercise.exercise)
        await state.update_data(exercise=diary.exercise)
        await state.set_state(AddExercise.approach)
        await state.update_data(approach=1)
        await state.set_state(AddExercise.diary_id)
        await state.update_data(diary_id=diary.id)
        await state.set_state(AddExercise.count_exercise)
        await state.update_data(count_exercise=1)
        await state.set_state(AddExercise.rest)
        await state.update_data(rest=diary.rest)

        await call.message.answer(
            f"Тренировка началась\n\n1. {diary.exercise.capitalize()}\n\n1 подход\n ",
            reply_markup=get_button_by_exercies(),
        )

        await bot.send_message(
            chat_id=telegram, text="Введите количество сделанных повторений"
        )

        await state.set_state(AddExercise.start_time)
    else:
        if settings.exercise_list:
            diary = settings.exercise_list.pop(0)
            await state.set_state(AddExercise.exercise)
            await state.update_data(exercise=diary.exercise)
            await state.set_state(AddExercise.approach)
            await state.update_data(approach=1)
            await state.set_state(AddExercise.diary_id)
            await state.update_data(diary_id=diary.id)
            await state.set_state(AddExercise.rest)
            await state.update_data(rest=diary.rest)

            data = await state.get_data()
            count_exercise = data["count_exercise"] + 1
            await state.set_state(AddExercise.count_exercise)
            await state.update_data(count_exercise=count_exercise)

            await call.message.answer(
                f"{count_exercise}. {diary.exercise.capitalize()}\n\n1 подход\n",
                reply_markup=get_button_by_exercies(),
            )

            await bot.send_message(
                chat_id=telegram, text="Введите количество сделанных повторений"
            )

            await state.set_state(AddExercise.start_time)
        else:
            settings.start_exercise = True
            settings.exercise_list = []
            await state.clear()
            await call.message.answer(
                "Тренировка окончена\nДанные записаны в дневник",
                reply_markup=get_menu_reply_kb(),
            )


@router.message(StateFilter("*"), F.text == "<<Отменa>>")
async def cancel_exercise_handler(message: Message, state: FSMContext):
    """Реакция бота на нажатие <<Отмена>>."""
    current_state = await state.get_state()

    if current_state is None:
        return

    settings.start_exercise = True
    settings.exercise_list = []
    await state.clear()
    await message.answer(
        "Тренировка отменена\n\nДневник тренировок",
        reply_markup=get_menu_reply_kb(),
    )


@router.callback_query(AddExercise.end_time, F.data == "approach_+")
async def add_approach(call: CallbackQuery, state: FSMContext):
    """Реакция бот на approach_+."""
    data = await state.get_data()
    approach = data["approach"] + 1

    await state.set_state(AddExercise.approach)
    await state.update_data(approach=approach)

    await call.message.answer(
        f"{approach} подход\n\nВведите количество сделанных повторений"
    )
    await state.set_state(AddExercise.start_time)


@router.message(AddExercise.start_time, F.text)
async def start_rest(message: Message, state: FSMContext):
    """Реакция бота на введние пользователем количество повторений в упражнении."""
    data = await state.get_data()
    repetition = message.text

    repetition = chek_data_by_int(repetition)
    if repetition:
        await state.set_state(AddExercise.repetition)
        await state.update_data(repetition=int(message.text))
        await state.set_state(AddExercise.start_time)
        await state.update_data(start_time=time.time())

        rest = removes_the_last_zeros(data["rest"])

        await message.answer(
            f"Время отдыха {rest} м.\n\nНапечатайте любой символ по истечении времени отдыха, чтобы продолжить тренировку или нажмите 'пропустить отдых'",
            reply_markup=get_button_by_exercies(rest=True,)

        )

        await state.set_state(AddExercise.end_time)
    else:
        await message.answer(
            "Количество повторений должно быть числом\n\nВведите количество сделанных повторений"
        )


@router.message(AddExercise.end_time, F.text)
async def end_rest(message: Message, state: FSMContext):
    """Добавление упражнения в дневник."""
    data = await state.get_data()
    rest = data["rest"] * 60
    start_time = data["start_time"]
    end_time = time.time()

    result_time = end_time - start_time
    print(result_time)
    print(rest)
    if result_time > rest or message.text == "пропустить отдых":
        data = await state.get_data()
        exercise = data["exercise"]
        approach = data["approach"]
        diary_id = data["diary_id"]
        repetition = data["repetition"]
        exercise = ExerciesSQLAlchemyRepository().add_exercise(
            exercise=exercise,
            approach=approach,
            diary_id=diary_id,
            repetition=repetition,
        )

        user = UserSQAlchemyRepository().get_user(telegram=int(message.chat.id))
        diary = DiarySQLAlchemyRepository().get_diary_by_id(
            user_id=user.id,
            diary_id=diary_id,
        )
        DiarySQLAlchemyRepository().update_diary_by_completed(
            diary_id=diary_id,
            completed=True,
            total_approach=approach,
            total_repetition=diary.total_repetition + repetition,
        )

        await message.answer(
            "Хотите сделать еще один подход ?",
            reply_markup=get_buttons_add_a_approach(),
        )
    else:
        rest = removes_the_last_zeros(data["rest"])
        await message.answer(
            f"Прошло {int(result_time)} c.\n\n{rest} м. еще не закончились\n\nНапечатайте любой символ по истечении времени отдыха, чтобы продолжить тренировку или нажмите 'пропустить отдых'",
            reply_markup=get_button_by_exercies(rest=True)
        )
