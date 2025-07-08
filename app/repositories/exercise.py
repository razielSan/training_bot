from models import Exercise
from models.db_helper import db_helper


class ExerciesSQLAlchemyRepository:
    """Репозиторий для упражнения."""
    model: Exercise

    def add_exercise(
        self,
        exercise: str,
        approach: int,
        repetition: int,
        diary_id: int,
    ):
        try:
            with db_helper.get_session() as session:
                exercise = Exercise(
                    exercise=exercise,
                    approach=approach,
                    repetition=repetition,
                    diary_id=diary_id,
                )
                session.add(exercise)
                session.commit()
        except Exception as err:
            session.rollback()
            print(err)

    def delete_exercise(self, diary_id: int):
        try:
            with db_helper.get_session() as session:
                add = session.query(Exercise).filter_by(diary_id == diary_id).delete()
                session.commit()
                return True
        except Exception as err:
            print(err)

