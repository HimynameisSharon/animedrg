import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Try to find the .env file path
env_path = Path(__file__).resolve().parent / ".env"

# Load the file ONLY if it actually exists (Local Laptop Mode)
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Otherwise, just load from the system environment (Render Cloud Mode)
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Check if the variables are actually loaded
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(f"Missing SUPABASE_URL or SUPABASE_ANON_KEY. URL found: {bool(SUPABASE_URL)}, Key found: {bool(SUPABASE_KEY)}")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)