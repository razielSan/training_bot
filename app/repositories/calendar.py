from calendar import monthrange
from datetime import datetime

from sqlalchemy import extract

from models import Calendar
from models.db_helper import db_helper
from config import settings


class CalendarSQLAlchemyRepository:
    """Репозиторий для календаря."""
    model = Calendar

    def add_calendar(
        self,
        year: str,
        month: str,
        count_days: str,
    ):
        """Добавление календаря."""
        with db_helper.get_session() as session:
            try:
                days = monthrange(int(year), int(month))[1]
                if days == int(count_days):
                    calendar = Calendar(
                        year=int(year),
                        month=int(month),
                        month_name=settings.month[int(month)],
                        count_days=int(count_days),
                        date=datetime(int(year), int(month), 1),
                    )
                    session.add(calendar)
                    session.commit()
                    return (
                        True,
                        {"error": None},
                    )
                else:
                    return (
                        False,
                        {"error": "Неправильно введеное количество дней"},
                    )
            except Exception as err:
                session.rollback()
                return (
                    False,
                    {"error": str(err)},
                )

    def get_calendar_all(self):
        """Возвращает все записи из календаря."""
        with db_helper.get_session() as session:
            calendar = session.query(Calendar).all()
            return calendar

    def get_calendar_by_date(self, year: int, month: int):
        """Возвращает календарь по дате и месяцу."""
        with db_helper.get_session() as session:
            calendar = (
                session.query(Calendar)
                .filter_by(
                    year=year,
                    month=month,
                )
                .first()
            )
            return calendar

    def get_calendars_by_filters(self, year: int, month: int, flag: str):
        """Bозвращает календари которые больше или меньше указанного года и месяца."""
        with db_helper.get_session() as session:
            if flag == "+":
                calendaries = (
                    session.query(Calendar)
                    .filter(Calendar.date > datetime(year, month, 1))
                    .all()
                )
                return calendaries
            else:
                calendaries = (
                    session.query(Calendar)
                    .filter(Calendar.date < datetime(year, month, 1))
                    .all()
                )
                return calendaries
