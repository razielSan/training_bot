from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import settings


class DataBaseHelper:
    """Помощник для базы данных."""
    def __init__(self):
        self.engine = create_engine(url=settings.SQL_URL)
        self.session_factory = sessionmaker(
            bind=self.engine,
        )

    def get_session(self):
        with self.session_factory() as session:
            return session


db_helper = DataBaseHelper()

