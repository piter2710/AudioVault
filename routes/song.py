from datetime import datetime
from typing import Annotated
import uuid
from fastapi.responses import RedirectResponse
from fastapi import Form
from .auth import current_user_dep
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from database import database_connection
from models.Song import Song as SongModel
from schemas.Song import SongCreate, SongOut
from models.Tag import Tag as TagModel
from sqlalchemy import select
from services.storage import SupabaseStorageService
router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("/", response_model=list[SongOut])
async def get_all_songs(start: int, end: int, db: database_connection):
    if end <= start or start < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")
    stmt = select(SongModel).offset(start).limit(end - start)
    result = await db.execute(stmt)
    songs = result.scalars().all()
    return songs

@router.get("/{song_id}", response_model=SongOut)
async def get_song(song_id: int, db: database_connection):
    stmt = select(SongModel).where(SongModel.song_id == song_id)
    result = await db.execute(stmt)
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    return song

@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(song_id: int, current_user: current_user_dep, db: database_connection, service: storage_service_dep):
    stmt = select(SongModel).where(SongModel.song_id == song_id)
    result = await db.execute(stmt)
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    if song.publisher_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this song")
    try:
        await db.delete(song)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting song from database")
    try:
        await service.delete_file(song.song_path)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting song from storage service")

    return None

@router.get("/me", response_model=list[SongOut])
async def get_my_songs(current_user: current_user_dep, db: database_connection):
    stmt = select(SongModel).where(SongModel.publisher_id == current_user.user_id)
    result = await db.execute(stmt)
    songs = result.scalars().all()
    return songs

@router.get("/user/{user_id}", response_model=list[SongOut])
async def get_user_songs(user_id: int, db: database_connection):
    stmt = select(SongModel).where(SongModel.publisher_id == user_id)
    result = await db.execute(stmt)
    songs = result.scalars().all()
    return songs

def get_storage_service() -> SupabaseStorageService:
    return SupabaseStorageService()
storage_service_dep = Depends(get_storage_service)


@router.post("/", response_model=SongOut)
async def post_song(file: UploadFile, song: Annotated[SongCreate, Form()], current_user: current_user_dep, db: database_connection, service: storage_service_dep) -> SongOut:
    #TODO: generate song path using external service and ensure it's unique for each song
    audio_extensions = ["mp3", "wav", "flac", "aac", "ogg", "m4a"]
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error reading uploaded file")
    try:
        extension = file.filename.split(".")[-1]
        if extension not in audio_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only audio files are allowed.")
        unique_path = f"uploads/{current_user.user_id}/{uuid.uuid4()}.{extension}"
        
        await service.upload_file(file_bytes, unique_path, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error uploading file to storage service")

    song_path = unique_path
    unique_tag_ids = list(set(song.tag_ids))
    tags_stmt = select(TagModel).where(TagModel.tag_id.in_(unique_tag_ids))
    tags_result = await db.execute(tags_stmt)
    tags = tags_result.scalars().all()
    if len(tags) != len(unique_tag_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more tags do not exist")
    new_song = SongModel(title=song.title, publisher_id=current_user.user_id, song_path=song_path)
    new_song.tags = tags
    #In case of database error we need to delete the uploaded file to avoid garbage in the storage.
    try:
        db.add(new_song)
        await db.commit()
        await db.refresh(new_song)
    except Exception as e:
        await service.delete_file(song_path)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving song to database")
    return SongOut(
        song_id=new_song.song_id,
        title=new_song.title,
        publisher_id=new_song.publisher_id,
        song_path=new_song.song_path
    )

@router.get("/download/{song_id}")
async def download_song(song_id: int, current_user: current_user_dep, db: database_connection, service: storage_service_dep):
    #The unused current_user_dep is used only for the download to be accesible for logged in users.
    #The issue of anyone knowing the url for now is not a problem since the urls are signed and expire after a short time, 
    stmt = select(SongModel).where(SongModel.song_id == song_id)
    result = await db.execute(stmt)
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    signed_url = await service.create_signed_url(song.song_path, expires_in=600)
    #For now redirecting maybe later on simple URL to use in the front-end
    return RedirectResponse(signed_url)
    
@router.get("/analyze/{song_id}")
async def analyze_song(song_id: int, current_user: current_user_dep, db: database_connection):
    stmt = select(SongModel).where(SongModel.song_id == song_id)
    result = await db.execute(stmt)
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    if song.publisher_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to analyze this song")
    
    #TODO: implement song analysis to let the user check the tags of the song and suggest new ones based on the audio content