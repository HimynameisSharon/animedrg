import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# This makes sure .env is always found regardless of where Python is run from
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("https://hesfclkqlmfinlcepdps.supabase.co")
SUPABASE_KEY = os.getenv("SeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhlc2ZjbGtxbG1maW5sY2VwZHBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU1MDkwNTMsImV4cCI6MjA5MTA4NTA1M30.f8Pd-N5ru8OJ0dY0jEpe89uhZgVfYpp95zmC6c8LGfUUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in your .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)