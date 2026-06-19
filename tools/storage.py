import asyncio
from functools import partial
from supabase import create_client, Client
from settings import settings

def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

async def run_sync(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))

class SupabaseStorageService:
    def __init__(self):
        self.client = get_supabase_client()
        self.bucket_name = settings.BUCKET_NAME

    async def upload_file(self,file_bytes: bytes, file_path: str, content_type: str) -> dict:
        response = await run_sync(
            self.client.storage.from_(self.bucket_name).upload,
            file_path,
            file_bytes,
            file_options={"content_type": content_type,"upsert": True}
        )
        if response.get("error"):
            raise Exception(f"Supabase upload error: {response['error']['message']}")
        return {"file_path": file_path, "content_type": content_type}

    async def get_public_url(self, file_path: str) -> str:
        """Get a permanent public URL (bucket must be public)."""
        result = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
        return result

    async def create_signed_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get a temporary signed URL (works for private buckets)."""
        result = await run_sync(
            self.client.storage.from_(self.bucket_name).create_signed_url,
            file_path,
            expires_in,
        )
        return result["signedURL"]

    async def delete_file(self, file_path: str) -> dict:
        result = await run_sync(
            self.client.storage.from_(self.bucket_name).remove,
            [file_path],
        )
        return result

    async def list_files(self, folder: str = "") -> list:
        result = await run_sync(
            self.client.storage.from_(self.bucket_name).list,
            folder,
        )
        return result