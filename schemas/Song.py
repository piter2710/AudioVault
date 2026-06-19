from pydantic import BaseModel, ConfigDict
from typing import List
from schemas.Tag import TagOut

class SongBase(BaseModel):
    title: str

class SongCreate(SongBase):
    tag_ids: List[int] = []

class SongOut(SongBase):
    song_id: int
    publisher_id: int
    song_path: str
    tags: List[TagOut] = []

    model_config = ConfigDict(from_attributes=True)
