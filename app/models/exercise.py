from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func, ForeignKey

from extensions import Base


class Exercise(Base):
    """Модель для упражнений."""

    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise: Mapped[str]  # Название упражнения
    approach: Mapped[int]  # подход
    repetition: Mapped[int]  # повторение

    diary_id: Mapped[int] = mapped_column(ForeignKey("diary.id", ondelete="CASCADE"), )
    diary: Mapped["Diary"] = relationship(
        back_populates="exercise_detail",
        lazy="subquery",
    )
