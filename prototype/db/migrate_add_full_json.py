import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

MIGRATION_SQL = """
ALTER TABLE worlds ADD COLUMN IF NOT EXISTS full_json JSONB;
"""

def main():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute(MIGRATION_SQL)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Migration complete: full_json column added to worlds table (if not already present).")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    main() 