"""Backend bootstrap helpers.

Run this once to create the SQLite tables:

    python -m backend.main

The three runnable processes of this project are:
    1. MCP server : python -m backend.mcp_server.mcp
    2. Voice bot  : python -m backend.pipecat.voice_to_text
    3. Frontend   : (see ../frontend)  npm run dev
"""

from backend.db.connection import init_db


def main():
    init_db()
    print("Database initialized (tables created).")


if __name__ == "__main__":
    main()
