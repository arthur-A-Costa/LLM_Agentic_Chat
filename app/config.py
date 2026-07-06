import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env", override=False)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres_user:postgres_password@postgres:5432/postgres"
)