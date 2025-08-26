import os
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY not loaded from .env")
if not ASSEMBLYAI_API_KEY:
    print("⚠️ Warning: ASSEMBLYAI_API_KEY not loaded from .env")
if not MURF_API_KEY:
    print("⚠️ Warning: MURF_API_KEY not loaded from .env")
if not TAVILY_API_KEY:
    print("⚠️ Warning: TAVILY_API_KEY not loaded from .env")