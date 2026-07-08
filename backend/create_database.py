"""Initialize the SQLite database using the canonical schema in database.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import DB_PATH, init_db

if __name__ == "__main__":
    init_db()
    print(f"Database initialized successfully at: {DB_PATH}")
