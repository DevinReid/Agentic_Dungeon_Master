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

    # 🚀 Drop table first (wipes existing data!)
    cur.execute("DROP TABLE IF EXISTS characters;")

    # 🚀 Create table fresh
    cur.execute("""
        CREATE TABLE characters (
            id SERIAL PRIMARY KEY,
            name TEXT,
            class TEXT,
            hp INTEGER,
            strength INTEGER,
            dexterity INTEGER,
            constitution INTEGER,
            intelligence INTEGER,
            wisdom INTEGER,
            charisma INTEGER,
            level INTEGER,
            experience INTEGER,
            ac INTEGER
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
    cur.execute("""
        SELECT name, class, hp, strength, dexterity, constitution,
               intelligence, wisdom, charisma, level, experience, ac
        FROM characters LIMIT 1;
    """)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result


def update_character_stats(name: str, stats: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE characters
        SET strength=%s, dexterity=%s, constitution=%s,
            intelligence=%s, wisdom=%s, charisma=%s,
            level=%s, experience=%s, hp=%s, ac=%s
        WHERE name=%s;
    """, (
        stats["strength"], stats["dexterity"], stats["constitution"],
        stats["intelligence"], stats["wisdom"], stats["charisma"],
        stats["level"], stats["experience"], stats["hp"], stats["ac"], name
    ))
    conn.commit()
    cur.close()
    conn.close()

