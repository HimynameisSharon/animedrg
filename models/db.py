import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# This handles both Local (with .env) and Render (Dashboard variables)
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in Environment")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)