import os
from dotenv import load_dotenv

# Load .env once (safe even if already loaded)
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found. Check your .env file")
