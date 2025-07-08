from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func, ForeignKey

from extensions import Base


class Diary(Base):
    """Модель для дневника тренировок."""

    __tablename__ = "diary"

    id: Mapped[int] = mapped_column(primary_key=True)
    training_count: Mapped[int] = mapped_column(
        default=0
    )  # какая по счету тренировка в день
    exercise_count: Mapped[int] = mapped_column(default=1)  # какое по счету упражнение
    total_approach: Mapped[int] = mapped_column(default=1)  # общее количество подходов
    total_repetition: Mapped[int] = mapped_column(
        default=0
    )  # Общее количество повторений
    rest: Mapped[float]  # отдых
    exercise: Mapped[str]  # название упражнения
    completed: Mapped[bool] = mapped_column(
        default=False
    )  # Флаг проверки завершенности упражнения

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="diaries")

    calendardays_id: Mapped[int] = mapped_column(ForeignKey("calendardays.id"))
    calendar_day: Mapped["CalendarDays"] = relationship(
        back_populates="training_records"
    )

    exercise_detail: Mapped[List["Exercise"]] = relationship(
        back_populates="diary", lazy="subquery", cascade="all, delete", 
        passive_deletes=True,
    )

    date: Mapped[DateTime] = mapped_column(DateTime, default=func.now())  # время\

    def __str__(self):
        return str(f"Diary(user_id={self.user_id})")
