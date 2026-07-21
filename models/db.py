import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Go UP two levels (.parent.parent) to reach the root 'animedrg/' folder where .env lives
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Pass the KEY NAMES into os.getenv(), not the actual values
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in your .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)