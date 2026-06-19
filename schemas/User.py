from pydantic import BaseModel, ConfigDict
from typing import List
from schemas.Song import SongOut

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class UserWithSongs(UserOut):
    songs: List[SongOut] = []

class UserWithLikes(UserOut):
    liked_songs: List[SongOut] = []

