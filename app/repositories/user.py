from models.db_helper import db_helper
from models import User


class UserSQAlchemyRepository:
    """Репозиторий для пользователя."""
    model = User

    def create_user(
        self,
        name: str,
        telegram: int,
        status="user",
    ):
        """Создает пользователя в модели User.
        Возвращает пользователя если создан или None если нет
        """
        with db_helper.get_session() as session:

            try:
                user = User(
                    name=name,
                    telegram=telegram,
                    status=status,
                )

                session.add(user)
                session.commit()
                return True
            except Exception as err:                
                session.rollback()
                print(err)
                return None

    def get_user(self, telegram: int):
        """Ищет пользователя в модели User."""
        with db_helper.get_session() as session:
            try:
                user = session.query(User).filter_by(telegram=telegram).first()
                return user
            except Exception as err:
                print(err)
                return None
