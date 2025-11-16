import uuid
import mimetypes
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from supabase_client import supabase  # keep your existing import

class SupabaseStorage(Storage):
    """
    Django Storage backend for Supabase Storage.
    Ensures bytes are uploaded and the correct content-type is set.
    """

    bucket_name = "bms"

    def _save(self, name, content):
        # Keep folder path from Django's upload_to
        folder = ""
        if "/" in name:
            folder, orig_name = name.rsplit("/", 1)
        else:
            orig_name = name

        ext = orig_name.split(".")[-1] if "." in orig_name else ""
        unique_name = f"{uuid.uuid4()}{('.' + ext) if ext else ''}"
        final_name = f"{folder}/{unique_name}" if folder else unique_name

        # Read file content as bytes (support UploadedFile.chunks)
        if hasattr(content, "chunks"):
            chunks = []
            for chunk in content.chunks():
                # chunk may be bytes already
                if isinstance(chunk, str):
                    chunk = chunk.encode("utf-8")
                chunks.append(chunk)
            data = b"".join(chunks)
        elif hasattr(content, "read"):
            data = content.read()
            if isinstance(data, str):
                data = data.encode("utf-8")
        else:
            # content could be raw bytes or bytearray
            data = content
            if isinstance(data, str):
                data = data.encode("utf-8")

        if isinstance(data, bytearray):
            data = bytes(data)

        # Guess MIME type (prefer original filename) and fallback to any content_type provided by Django UploadedFile
        mime_type, _ = mimetypes.guess_type(orig_name)
        if not mime_type and hasattr(content, "content_type"):
            mime_type = getattr(content, "content_type", None)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Upload to Supabase; pass content_type so Supabase stores correct MIME
        try:
            # Many supabase-python wrappers accept content_type kwarg.
            # If yours uses a different signature, adapt this call accordingly.
            supabase.storage.from_(self.bucket_name).upload(final_name, data, content_type=mime_type)
        except TypeError:
            # fallback if the client expects a dict of options or a different kwarg name
            supabase.storage.from_(self.bucket_name).upload(final_name, data, {"content-type": mime_type})
        except Exception as e:
            # bubble up a helpful error for debugging
            raise RuntimeError(f"Supabase upload failed for {final_name}: {e}") from e

        # Return stored path that Django will save on the model
        return final_name

    def exists(self, name):
        try:
            files = supabase.storage.from_(self.bucket_name).list()
        except Exception:
            # if listing fails, conservatively return False
            return False
        return any(f.get("name") == name for f in files)

    def delete(self, name):
        try:
            supabase.storage.from_(self.bucket_name).remove([name])
        except Exception as e:
            # ignore or log; Django expects delete to be idempotent
            # You can raise if you prefer strict behaviour
            pass

    def url(self, name):
        # get_public_url often returns a dict with key 'publicURL' or 'publicUrl'
        url_or_dict = supabase.storage.from_(self.bucket_name).get_public_url(name)
        if isinstance(url_or_dict, dict):
            return url_or_dict.get("publicURL") or url_or_dict.get("publicUrl")
        return url_or_dict

    def _open(self, name, mode="rb"):
        # download should return bytes (or raise)
        data = supabase.storage.from_(self.bucket_name).download(name)
        if isinstance(data, dict) and data.get("error"):
            raise IOError(f"Failed to download {name}: {data.get('error')}")
        if isinstance(data, str):
            data = data.encode("utf-8")
        return ContentFile(data)
