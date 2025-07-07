from typing import List, Dict, Tuple

from pydantic_settings import BaseSettings, SettingsConfigDict
from aiogram.types import BotCommand


class Settings(BaseSettings):
    """Настройки для бота."""
    TOKEN: str
    SQL_URL: str
    command_list: List = [
        BotCommand(command="start", description="меню бота"),
        BotCommand(command="admin", description="для админов"),
    ]
    exercise_count: int = (
        0  # настройка для узнавания какое по счету упражнение в тренировке
    )
    start_exercise: bool = True  # проверяет является ли тренировка только начавшейся
    exercise_list: List = []  # список тренировочных упражнений
    new_training: bool = True  # настройка для отслеживания является ли добавление записи в дневник новой тренировкой
    training_count: int = 0  # настройка для узнавания какая по счету тренировка в день
    count: int = 1  # счетчик
    plus_exercise: bool = False  # настройка для отслеживания является ли упражнение первым добавленным или нет
    date_trainer: str = ""  # Настройка для отслеживания даты тренировки чтобы не пришлось вводит второй раз
    hour: int = 0  # Настройка для отслеживания часа начала тренировки чтобы не пришлось вводит второй раз
    month: Dict = {
        1: "январь",
        2: "февраль",
        3: "март",
        4: "апрель",
        5: "май",
        6: "июнь",
        7: "июль",
        8: "август",
        9: "сентябрь",
        10: "октябрь",
        11: "ноябрь",
        12: "декабрь",
    }  # настройка для узнавания названия месяца по числу
    day_week: Tuple = (
        "Пн",
        "Вт",
        "Ср",
        "Чт",
        "Пт",
        "Сб",
        "Вс",
    )  # кортеж месяцев для календаря

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
