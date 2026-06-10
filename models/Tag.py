from typing import TYPE_CHECKING
from sqlalchemy import Integer, String
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.Song import Song

class Tag(Base):
    __tablename__ = "tags"
    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    songs: Mapped[list["Song"]] = relationship(secondary="song_tags", back_populates="tags")