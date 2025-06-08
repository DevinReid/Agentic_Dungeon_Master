import os
import psycopg2
from dotenv import load_dotenv
from db import init_db

load_dotenv()

# Connection to the default 'postgres' DB to create new DB
POSTGRES_URL = os.getenv("POSTGRES_URL")  # e.g. postgresql://postgres:password@localhost:5432/postgres
GAME_DB_NAME = os.getenv("GAME_DB_NAME", "agentic_dnd")

def create_game_database():
    conn = psycopg2.connect(POSTGRES_URL)
    conn.autocommit = True  # To run CREATE DATABASE command
    cur = conn.cursor()

    # Check if DB already exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (GAME_DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {GAME_DB_NAME};")
        print(f"Database '{GAME_DB_NAME}' created successfully.")
    else:
        print(f"Database '{GAME_DB_NAME}' already exists.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    create_game_database()
    # Now that the DB exists, initialize the schema
    init_db()
    print("Database and tables are set up and ready to go!")
