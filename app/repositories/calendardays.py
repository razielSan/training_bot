from datetime import datetime

from sqlalchemy import extract

from models import CalendarDays
from models.db_helper import db_helper


class CalendarDaysSQLAlchemyRepository:
    """Репозиторий для календарных дней."""
    model: CalendarDays

    def add_calendar_days(
        self,
        count_day: int,
        calendar_id: int,
        year: int,
        month: int,
    ):
        """Заполняет указаный месяц в году календарными днями."""
        with db_helper.get_session() as session:
            try:
                for day in range(1, count_day + 1):
                    session.add(
                        CalendarDays(
                            day=day,
                            date=datetime(year, month, day),
                            calendar_id=calendar_id,
                        )
                    )
                session.commit()
            except Exception as err:
                print(err)

    def get_calendar_days(self, date: datetime):
        """Возвращает календарные дни месяца."""
        with db_helper.get_session() as session:
            calendar = (
                session.query(CalendarDays)
                .filter(
                    CalendarDays.date == date,
                )
                .first()
            )
            return calendar

 