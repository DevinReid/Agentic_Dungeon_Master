#!/usr/bin/env python3
"""
Cleanup script to remove the extra campaign databases and prepare for proper schema
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def cleanup_campaign_databases():
    """Remove all the extra campaign databases we created"""
    print("🧹 CLEANING UP CAMPAIGN DATABASES")
    print("=" * 50)
    
    # Connect to postgres default database to manage other databases
    postgres_base = DB_URL.rsplit('/', 1)[0] + '/postgres'
    
    try:
        conn = psycopg2.connect(postgres_base)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Find all campaign databases
        print("\n1. Finding campaign databases...")
        cur.execute("""
            SELECT datname FROM pg_database 
            WHERE datname LIKE 'campaign_%';
        """)
        
        campaign_dbs = cur.fetchall()
        
        if campaign_dbs:
            print(f"Found {len(campaign_dbs)} campaign databases:")
            for (db_name,) in campaign_dbs:
                print(f"  - {db_name}")
            
            # Drop each campaign database
            print("\n2. Dropping campaign databases...")
            for (db_name,) in campaign_dbs:
                try:
                    # Terminate connections to the database first
                    cur.execute(f"""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = '{db_name}' AND pid <> pg_backend_pid();
                    """)
                    
                    # Drop the database
                    cur.execute(f'DROP DATABASE IF EXISTS "{db_name}";')
                    print(f"  ✅ Dropped {db_name}")
                except Exception as e:
                    print(f"  ❌ Failed to drop {db_name}: {e}")
        else:
            print("No campaign databases found to clean up.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False
    
    print("\n3. Checking main database...")
    try:
        # Check main database exists
        main_conn = psycopg2.connect(DB_URL)
        main_conn.close()
        print("✅ Main agentic_dnd database is accessible")
    except Exception as e:
        print(f"❌ Cannot access main database: {e}")
        return False
    
    print("\n✅ Cleanup complete!")
    print("\n🎯 NEXT STEPS:")
    print("1. Run: python db/db_schema.py  (to create proper schema)")
    print("2. All data will live in one database with campaign_id columns")
    print("3. Much cleaner and more scalable!")
    
    return True

if __name__ == "__main__":
    cleanup_campaign_databases() 