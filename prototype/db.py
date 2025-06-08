import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
  # E.g. postgres://user:pass@localhost/dbname

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create characters table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id SERIAL PRIMARY KEY,
            name TEXT,
            class TEXT,
            hp INTEGER
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def clear_characters():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM characters;")
    conn.commit()
    cur.close()
    conn.close()

def create_character(name: str, char_class: str, hp: int = 30):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO characters (name, class, hp) VALUES (%s, %s, %s);",
        (name, char_class, hp)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_character_sheet():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, class, hp FROM characters LIMIT 1;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result  # Tuple: (name, class, hp)
