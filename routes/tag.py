from fastapi import APIRouter, Depends, HTTPException, status
from database import database_connection
from models.Tag import Tag as TagModel
from schemas.Tag import TagCreate, TagOut
from sqlalchemy import select
from .auth import current_user_dep
router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/", response_model=list[TagOut])
async def get_all_tags(start: int, end: int, db: database_connection):
    stmt = select(TagModel).offset(start).limit(end - start)
    result = await db.execute(stmt)
    tags = result.scalars().all()
    return tags
@router.post("/", response_model=TagOut)
async def create_tag(tag: TagCreate, current_user: current_user_dep, db: database_connection) -> TagOut:
    upper_tag_name = tag.name.upper()
    new_tag = TagModel(name=upper_tag_name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag
@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, current_user: current_user_dep, db: database_connection):
    stmt = select(TagModel).where(TagModel.tag_id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    await db.delete(tag)
    await db.commit()
    return None
@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(tag_id: int, db: database_connection):
    stmt = select(TagModel).where(TagModel.tag_id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
@router.patch("/{tag_id}", response_model=TagOut)
async def update_tag(tag_id: int, tag_update: TagCreate, current_user: current_user_dep, db: database_connection):
    stmt = select(TagModel).where(TagModel.tag_id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    tag.name = tag_update.name
    await db.commit()
    await db.refresh(tag)
    return tag