from datetime import datetime

from sqlalchemy import extract, desc, func, select, text


from models import Diary
from models.db_helper import db_helper


class DiarySQLAlchemyRepository:
    """Репозиторий для дневника."""

    model: Diary

    async def create_diairy(
        self,
        exercise: str,
        rest: float,
        date: datetime,
        user_id: int,
        calendardays_id: int,
        training_count=1,
        exercise_count=1,
        total_approach=1,
        total_repetition=0,
    ):
        """Создание дневника в модели Diary
        Возвращает diary если создан или None если нет
        """

        with db_helper.get_session() as session:
            try:
                data = Diary(
                    exercise=exercise,
                    rest=rest,
                    date=date,
                    user_id=user_id,
                    training_count=training_count,
                    exercise_count=exercise_count,
                    total_approach=total_approach,
                    total_repetition=total_repetition,
                    calendardays_id=calendardays_id,
                )
                session.add(data)
                session.commit()

                return True
            except Exception as err:
                session.rollback()
                print(err)
                return None

    def get_diary(
        self,
        date: datetime,
        user_id: int,
        training_count: int,
    ):
        """Поиск дневника по дате и номеру тренировки."""
        try:
            with db_helper.get_session() as session:
                diary = (
                    session.query(Diary)
                    .filter(
                        Diary.date == date,
                        Diary.user_id == user_id,
                        Diary.training_count == training_count,
                    )
                    .order_by(Diary.exercise_count)
                    .all()
                )
                return diary
        except Exception as err:
            session.rollback()
            print(err)

    def get_diary_by_training_count(self, date: datetime, user_id: int):
        """Возвращает дневник по дате и фильтрует его по номеру тренировки."""
        with db_helper.get_session() as session:
            query = (
                select(
                    Diary.training_count,
                    func.count(Diary.training_count),
                )
                .where(
                    Diary.user_id == user_id,
                    extract("year", Diary.date) == date.year,
                    extract("month", Diary.date) == date.month,
                    extract("day", Diary.date) == date.day,
                )
                .group_by(Diary.training_count)
                .order_by(Diary.date)
            )
            result = session.execute(query).fetchall()
            return result

    def update_diary_by_completed(
        self,
        completed: bool,
        diary_id: int,
        total_repetition=0,
        total_approach=1,
    ):
        """Обновляет дневник."""
        with db_helper.get_session() as session:
            session.query(Diary).filter(Diary.id == diary_id).update(
                {
                    Diary.completed: completed,
                    Diary.total_repetition: total_repetition,
                    Diary.total_approach: total_approach,
                }
            )
            session.commit()

    def get_diary_by_id(
        self,
        user_id: int,
        diary_id: int,
    ):
        """Поиск дневника по id."""
        try:
            with db_helper.get_session() as session:
                diary = (
                    session.query(Diary)
                    .filter(Diary.user_id == user_id, Diary.id == diary_id)
                    .first()
                )
                return diary
        except Exception as err:
            session.rollback()
            print(err)

    def get_diary_by_date(
        self,
        date: datetime,
        user_id: int,
        training_count=False,
    ):
        """Поиск дневника по datetime
        training_count - сортирует по training_count
        """
        with db_helper.get_session() as session:
            try:

                dtime = datetime(
                    year=date.year,
                    month=date.month,
                    day=date.day,
                )

                if training_count:
                    diary = (
                        session.query(Diary)
                        .filter(
                            Diary.user_id == user_id,
                            extract("year", Diary.date) == dtime.year,
                            extract("month", Diary.date) == dtime.month,
                            extract("day", Diary.date) == dtime.day,
                        )
                        .order_by(Diary.training_count)
                        .all()
                    )
                else:
                    diary = (
                        session.query(Diary)
                        .filter(
                            Diary.user_id == user_id,
                            extract("year", Diary.date) == dtime.year,
                            extract("month", Diary.date) == dtime.month,
                            extract("day", Diary.date) == dtime.day,
                        )
                        .order_by(Diary.date)
                        .all()
                    )
                return diary
            except Exception as err:
                session.rollback()
                print(err)
                return None

    def get_list_day_for_diary(
        self,
        year: int,
        month: int,
        user_id: int,
    ):
        """Возвращает список тренировочных дней которые есть в этом указанном месяце"""
        with db_helper.get_session() as session:
            try:
                diary_list = (
                    session.query(Diary)
                    .filter(
                        Diary.user_id == user_id,
                        extract("year", Diary.date) == year,
                        extract("month", Diary.date) == month,
                    )
                    .all()
                )

                if diary_list:
                    return [diary.date.day for diary in diary_list]
                return None
            except Exception as err:
                session.rollback()
                print(err)

    def get_diary_list_all(self, user_id: int):
        """Возвращает список всех записей из дневника"""
        with db_helper.get_session() as session:
            try:
                list_diary = (
                    session.query(Diary)
                    .filter_by(user_id=user_id)
                    .order_by(
                        Diary.date,
                    )
                    .all()
                )
                return list_diary
            except Exception as err:
                session.rollback()
                print(err)

    def get_list_diaries_by_date(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        user_id: int,
        flag: str,
    ):
        """Возравщает записи из дневника которые больше или меньше указанных даныых"""

        with db_helper.get_session() as session:
            try:
                if flag == "+":
                    diaries = (
                        session.query(Diary)
                        .filter(
                            Diary.user_id == user_id,
                            Diary.date > datetime(year, month, day, hour),
                        )
                        .order_by(Diary.date)
                        .all()
                    )
                    return diaries
                else:
                    diaries = (
                        session.query(Diary)
                        .filter(
                            Diary.user_id == user_id,
                            Diary.date < datetime(year, month, day, hour),
                        )
                        .order_by(desc(Diary.date))
                        .all()
                    )
                    return diaries
            except Exception as err:
                session.rollback()
                print(err)

    def delete_diary(
        self,
        training_count: int,
        user_id: int,
        year: int,
        month: int,
        day: int,
        hour: int,
    ):
        """Удаление дневника"""

        with db_helper.get_session() as session:
            try:
                session.execute(text('PRAGMA foreign_keys=ON'))
                session.query(Diary).filter_by(
                    training_count=training_count,
                    user_id=user_id,
                    date=datetime(year, month, day, hour),
                ).delete()
                session.commit()
                return (True, {"error": None})
            except Exception as err:
                session.rollback()
                print(err)
                return (False, {"error": err})
