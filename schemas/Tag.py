from pydantic import BaseModel, ConfigDict

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    tag_id: int

    model_config = ConfigDict(from_attributes=True)
