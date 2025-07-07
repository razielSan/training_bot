from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger

from extensions import Base


class User(Base):
    """Модель для пользователя."""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    telegram: Mapped[int] = mapped_column(BigInteger, unique=True)
    status: Mapped[str] = mapped_column(default="user")

    diaries: Mapped[List["Diary"] ] = relationship(back_populates="user")
