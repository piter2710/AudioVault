from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.User import User
    from models.Tag import Tag

class Song(Base):
    __tablename__ = "songs"
    song_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    publisher_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    song_path: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    publisher: Mapped["User"] = relationship(back_populates="songs")
    tags: Mapped[list["Tag"]] = relationship(secondary="song_tags", back_populates="songs")

    liked_by_users: Mapped[list["User"]] = relationship(secondary="likes", back_populates="liked_songs")
    

