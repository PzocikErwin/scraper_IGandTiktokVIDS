import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "videos.db"
SESSIONS_DIR = BASE_DIR / ".sessions"
DOWNLOADS_DIR = BASE_DIR / "downloads"

# Ensure directories exist
SESSIONS_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Whisper Configuration
WHISPER_MODEL = "base" # Can be 'tiny', 'base', 'small', 'medium', 'large'

# Embeddings Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
