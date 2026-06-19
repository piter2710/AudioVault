from typing import TYPE_CHECKING
from sqlalchemy import String, Integer
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.Song import Song

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    songs: Mapped[list["Song"]] = relationship(back_populates="publisher")
    liked_songs: Mapped[list["Song"]] = relationship(secondary="likes", back_populates="liked_by_users")
