from sqlalchemy import Column, Integer, ForeignKey, Table
from database import Base

song_tags_table = Table(
    "song_tags",
    Base.metadata,
    Column("song_id", Integer, ForeignKey("songs.song_id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True),
)