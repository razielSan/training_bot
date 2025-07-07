from typing import List
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint

from models import Base


class Calendar(Base):
    """Модель для календаря."""
    __tablename__ = "calendar"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int]
    month: Mapped[int]
    month_name: Mapped[str]
    count_days: Mapped[int]
    date: Mapped[datetime]

    __table_args__ = (
        UniqueConstraint(
            "year",
            "month",
            name="uq_year_month",
        ),
    )

    days: Mapped[List["CalendarDays"]] = relationship(back_populates="calendar")
