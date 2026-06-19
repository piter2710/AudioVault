from sqlalchemy import Integer, String, ForeignKey, Column, Table
from database import Base

like_table = Table(
    "likes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.song_id"), primary_key=True),
)

