from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from models import Base


class CalendarDays(Base):
    """Модель для дней в календаре."""
    __tablename__ = "calendardays"

    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[int] 
    date: Mapped[datetime]

    calendar_id: Mapped[int] = mapped_column(ForeignKey("calendar.id"))
    calendar: Mapped["Calendar"] = relationship(back_populates="days")

    training_records: Mapped["Diary"] = relationship(back_populates="calendar_day")
