import os
import asyncio
from datetime import datetime
from pydantic import BaseModel
from ollama import AsyncClient
from settings import settings

class ChatResult(BaseModel):
    model: str
    user_query: str
    rules: str
    response: str
    created_at: datetime

async def convert_to_qwen_format(mp3_path: str) -> str:
    """
    Converts an MP3 into a 30-second, 16kHz, Mono WAV file.
    This is the strictly required format for local Ollama audio models.
    """
    wav_path = mp3_path.replace(".mp3", "_qwen.wav")
    
    command = [
        "ffmpeg", "-y", "-i", mp3_path,
        "-t", "30", "-ar", "16000", "-ac", "1",
        wav_path
    ]
    
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    return wav_path

async def analyze_music(user_query: str, song_location: str):
    rules = '''
    You are an expert music producer and audio analyst.
    Listen to the provided audio file.
    Return a clean JSON array containing exactly 5 highly specific genre, mood, or instrument tags.
    Do not return conversational text, only the tags.
    '''
    wav_file_path = await convert_to_qwen_format(song_location)
    client = AsyncClient(host=settings.OLLAMA_HOST)
    messages = [
        {"role": "system", "content": rules},
        {
            "role": "user", 
            "content": user_query,
            "images": [wav_file_path]
        }
    ]
    
    try:

        response = await client.chat(model="qwen2-audio", messages=messages)
        content = response['message']['content']
        
    finally:
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)
            
    return ChatResult(
        model="qwen2-audio",
        user_query=user_query,
        rules=rules,
        response=content,
        created_at=datetime.now()
    )