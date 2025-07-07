from datetime import datetime
from typing import List

from config import settings
from repositories.diary import DiarySQLAlchemyRepository


def chek_rest(rest: str):
    """Провяеряет являются время отдыха числом и находится в форрмате от 0 до 60."""
    try:
        data = float(rest)
        if -1 < data < 61:
            return (data, {"error": None})
        return (False, {"error": "Время отдыха должно быть в диапазоне от 0 до 60"})
    except Exception:
        return (False, {"error": "Время отдыха должно быть числом"})


def get_datetime_by_format(data: str):
    """ " Проверяет дату и время в формате - Год.Месяц.День."""
    try:
        year, month, day = data.split(".")

        date = datetime.now()
        if int(year) <= 0 or date > datetime(
            year=int(year),
            month=int(month),
            day=int(day),
        ):
            return (
                False,
                {
                    "error": "Введенные год, месяц и день не должны быть меньше текущей даты"
                },
            )

        dtime = datetime(
            year=int(year),
            month=int(month),
            day=int(day),
        )

        return (dtime, {"error": None})
    except Exception as err:
        print(err)
        if "year" in str(err):
            return (False, {"error": "Введенный год слишком большой"})
        if "convert" in str(err) or "invalid" in str(err):
            return (False, {"error": "Введенные данные должны быть числами"})
        elif "unpack" in str(err):
            return (False, {"error": "Некорректный формат вводаа"})
        elif "day is" in str(err):
            return (False, {"error": "Такого дня нет в этом месяце календаря"})
        elif "month" in str(err):
            return (False, {"error": "Месяц должен быть от 1 до 12"})


def check_hour(hour: str):
    """Провяряет являются час целым числом и находится в форрмате от 0 до 23."""
    try:
        hour = int(hour)
        if -1 < hour < 24:
            return (hour, {"error": None})
        return (False, {"error": "Час должен быть в диапазоне от 0 до 23"})
    except Exception:
        return (False, {"error": "Час должен быть целым числом"})


def get_training_info(
    list_diary: List,
    user_id: int,
):
    """Возвращает подробную информацию о тренировке."""
    split_left = "*" * 10
    split_right = "*" * 10

    all_list_diary = []
    date = list_diary[0].date
    info_training = (
        f"{split_left} {date.day}  {settings.month[date.month].capitalize()}  {date.year} {split_right}\n\n"
        f"Начало тренировки {date.hour} ч.\n\n"
        f"Завершенные упражнения\n"
    )

    all_list_diary.append(info_training)
    list_diary_not_completed = ["\nНезавершенные упражнения\n"]
    for diary in list_diary:
        if diary.completed:
            exercise_count = diary.exercise_count
            exercise_name = ""
            for exercise in diary.exercise_detail:
                if not exercise_name:
                    exercise_name = f"\n{exercise_count}. {exercise.exercise}\n\n"
                    all_list_diary.append(exercise_name)
                data_diary = (
                    f"{exercise.approach} подход    -     {exercise.repetition} повт.\n"
                )
                all_list_diary.append(data_diary)

            data_diary = f"\nОбщее количество подходов - {diary.total_approach}\nОбщее количество повторений - {diary.total_repetition}\n"
            all_list_diary.append(data_diary)
        else:
            list_diary_not_completed.append(f"{diary.exercise_count}. {exercise.exercise}\n")
    if len(list_diary_not_completed) == 1:
        list_diary_not_completed.append("\nВсе упражнения завершены")
    all_list_diary.extend(list_diary_not_completed)
    info_training = "".join(all_list_diary)
    return info_training


def get_training_data(
    list_diary: List,
    user_id: int,
):
    """Возвращает данные о тренировке."""
    split_left = "*" * 10
    split_right = "*" * 10
    ldiary = []
    diaries_data = []

    data = list_diary[0]
    result = DiarySQLAlchemyRepository().get_diary_by_training_count(
        user_id=user_id,
        date=datetime(year=data.date.year, month=data.date.month, day=data.date.day),
    )
    completed_diary_list = []
    for index, diary in enumerate(list_diary):
        if index == 0:
            ldiary.append(diary)

            count_training = 0
            for index, training_count in enumerate(result, start=1):
                if diary.training_count == training_count[0]:
                    count_training = index

            data = (
                f"{split_left} {ldiary[0].date.day}  {settings.month[ldiary[0].date.month].capitalize()}  {ldiary[0].date.year} {split_right}\n\n"
                f"{count_training} тренировка\n\n"
                f"Начало в {ldiary[0].date.hour} ч.\n\n"
                f"Упражнения"
            )
            diaries_data.append(data)
            diaries_data.append(f"{diary.exercise_count}. {diary.exercise}")
            completed_diary_list.append(diary)
        else:
            if diary.date == ldiary[0].date:
                diaries_data.append(f"{diary.exercise_count}. {diary.exercise}")
                completed_diary_list.append(diary)
            else:
                break

    completed = False
    for diary in completed_diary_list:
        if diary.completed:
            completed = True
            diaries_data.append("\n\nВы закончили эту тренировку")
            break

    data_training = "\n".join(diaries_data)
    return data_training, completed


def chek_data_by_int(data: int):
    """Проверяет является ли введенные данные числом."""
    try:
        data = float(data)
        return True
    except Exception:
        return False


def removes_the_last_zeros(digit: float):
    """Убирает последние ноли с числа."""
    data = str(digit).rstrip("0")
    digit = int(digit) if data[-1] == "." else float(digit)
    return digit
