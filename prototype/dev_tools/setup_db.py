import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add parent directory to path so we can import from db
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_schema import SCHEMA_SQL

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def setup_database():
    """Initialize database with all tables for persistent world data"""
    print("🚀 Setting up database with scalable schema...")
    print("   - Users table (for future multiplayer)")
    print("   - Campaigns table (campaign management)")
    print("   - Campaign_members table (access control)")
    print("   - Characters table (player data)")
    print("   - NPCs table (persistent characters)")  
    print("   - Locations table (world building)")
    print("   - Events table (story memory)")
    print("   - Relationships table (NPC allegiances)")
    
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Execute the schema directly from import
        cur.execute(SCHEMA_SQL)
        conn.commit()
        
        cur.close()
        conn.close()
        
        print("✅ Database setup complete!")
        print("\n🧠 AI Memory System Ready:")
        print("   → NPCs will remember past interactions")
        print("   → Story events will be stored for context")
        print("   → Relationships will persist between sessions")
        print("   → Campaign isolation ensures clean multiplayer")
        print("   → Scalable architecture ready for thousands of users")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False
    
    return True

if __name__ == "__main__":
    setup_database()
