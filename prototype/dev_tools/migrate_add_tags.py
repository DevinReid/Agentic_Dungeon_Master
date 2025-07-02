#!/usr/bin/env python3
"""
Migration: Add tags columns and tag_vocabulary table

This adds the tags functionality to existing tables without recreating them.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

MIGRATION_SQL = """
-- Add tags columns to existing tables
ALTER TABLE world_content ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
ALTER TABLE extracted_entities ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
ALTER TABLE npcs ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
ALTER TABLE locations ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';

-- Create tag_vocabulary table if it doesn't exist
CREATE TABLE IF NOT EXISTS tag_vocabulary (
    tag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    tag_name TEXT NOT NULL,
    tag_category TEXT,             -- 'entity', 'theme', 'category', 'location', 'relationship'
    usage_count INTEGER DEFAULT 1,
    first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, tag_name)  -- One tag per campaign (but different campaigns can have same tag)
);

-- Create GIN indexes for fast array searching (only if they don't exist)
CREATE INDEX IF NOT EXISTS idx_world_content_tags ON world_content USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_extracted_entities_tags ON extracted_entities USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_npcs_tags ON npcs USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_locations_tags ON locations USING GIN (tags);

-- Create indexes for tag_vocabulary
CREATE INDEX IF NOT EXISTS idx_tag_vocabulary_campaign ON tag_vocabulary(campaign_id);
CREATE INDEX IF NOT EXISTS idx_tag_vocabulary_category ON tag_vocabulary(tag_category);
CREATE INDEX IF NOT EXISTS idx_tag_vocabulary_usage ON tag_vocabulary(usage_count DESC);
"""

def run_migration():
    """Run the tags migration"""
    try:
        # Connect to database
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        
        print("🚀 Running tags migration...")
        
        # Execute migration SQL
        cur.execute(MIGRATION_SQL)
        
        # Commit changes
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Tags migration completed successfully!")
        print("\n🎯 Added:")
        print("   → tags TEXT[] column to world_content")
        print("   → tags TEXT[] column to extracted_entities") 
        print("   → tags TEXT[] column to npcs")
        print("   → tags TEXT[] column to locations")
        print("   → tag_vocabulary table for AI consistency")
        print("   → GIN indexes for fast tag array searching")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_migration() 