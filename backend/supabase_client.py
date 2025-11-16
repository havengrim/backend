from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role key for full access

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
