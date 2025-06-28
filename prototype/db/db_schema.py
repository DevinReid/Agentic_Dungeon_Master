#!/usr/bin/env python3
"""
Proper scalable database schema for the Agentic D&D system

This creates all tables in ONE database with proper campaign_id isolation.
Ready for thousands of users and campaigns.
"""

# SQL Schema for dev_tools/setup_db.py to import
SCHEMA_SQL = """
-- Drop existing tables in dependency order
DROP TABLE IF EXISTS relationships CASCADE;
DROP TABLE IF EXISTS events CASCADE;  
DROP TABLE IF EXISTS characters CASCADE;
DROP TABLE IF EXISTS npcs CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS campaign_members CASCADE;
DROP TABLE IF EXISTS campaigns CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. USERS TABLE - For future multiplayer
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CAMPAIGNS TABLE - Each campaign is isolated
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- 3. CAMPAIGN MEMBERS - Who has access to each campaign (future multiplayer)
CREATE TABLE campaign_members (
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role TEXT DEFAULT 'player',  -- 'dm', 'player'  
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (campaign_id, user_id)
);

-- 4. CHARACTERS - Player characters (isolated by campaign_id)
CREATE TABLE characters (
    character_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    class TEXT,
    level INTEGER DEFAULT 1,
    hp INTEGER DEFAULT 30,
    max_hp INTEGER DEFAULT 30,
    ac INTEGER DEFAULT 10,
    strength INTEGER DEFAULT 10,
    dexterity INTEGER DEFAULT 10,
    constitution INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    wisdom INTEGER DEFAULT 10,
    charisma INTEGER DEFAULT 10,
    experience INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, user_id)  -- One character per user per campaign
);

-- 5. LOCATIONS - Places in the world (isolated by campaign_id)
CREATE TABLE locations (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    connections JSONB,  -- Array of connected location IDs
    notable_features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. NPCS - Non-player characters (isolated by campaign_id)  
CREATE TABLE npcs (
    npc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    class TEXT,
    level INTEGER DEFAULT 1,
    hp INTEGER DEFAULT 10,
    max_hp INTEGER DEFAULT 10,
    ac INTEGER DEFAULT 10,
    strength INTEGER DEFAULT 10,
    dexterity INTEGER DEFAULT 10,
    constitution INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    wisdom INTEGER DEFAULT 10,
    charisma INTEGER DEFAULT 10,
    current_location_id UUID REFERENCES locations(location_id),
    status TEXT DEFAULT 'alive',  -- alive, dead, fled
    disposition TEXT DEFAULT 'neutral',  -- friendly, hostile, neutral
    backstory TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. EVENTS - Story events (isolated by campaign_id)
CREATE TABLE events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    event_type TEXT,  -- combat, conversation, discovery, etc.
    description TEXT NOT NULL,
    location_id UUID REFERENCES locations(location_id),
    npcs_involved JSONB,  -- Array of NPC IDs
    characters_involved JSONB,  -- Array of character IDs
    player_actions TEXT,
    consequences TEXT,
    session_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. RELATIONSHIPS - Character-NPC relationships (isolated by campaign_id)
CREATE TABLE relationships (
    relationship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    character_id UUID REFERENCES characters(character_id) ON DELETE CASCADE,
    npc_id UUID REFERENCES npcs(npc_id) ON DELETE CASCADE,
    relationship_type TEXT DEFAULT 'neutral',  -- ally, enemy, neutral, romantic
    relationship_score INTEGER DEFAULT 0,  -- -100 to +100
    history TEXT,
    last_interaction TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id, npc_id)  -- One relationship per character-npc pair
);

-- CREATE PERFORMANCE INDEXES

-- Campaign-based queries (most important - this is how isolation works!)
CREATE INDEX idx_characters_campaign ON characters(campaign_id);
CREATE INDEX idx_npcs_campaign ON npcs(campaign_id);
CREATE INDEX idx_events_campaign ON events(campaign_id);
CREATE INDEX idx_locations_campaign ON locations(campaign_id);
CREATE INDEX idx_relationships_campaign ON relationships(campaign_id);

-- User-based queries (for future multiplayer)
CREATE INDEX idx_characters_user ON characters(user_id);
CREATE INDEX idx_campaigns_creator ON campaigns(created_by);
CREATE INDEX idx_campaign_members_user ON campaign_members(user_id);

-- Location-based queries
CREATE INDEX idx_npcs_location ON npcs(current_location_id);

-- Time-based queries for recent events
CREATE INDEX idx_events_created ON events(created_at);
CREATE INDEX idx_relationships_updated ON relationships(updated_at);

-- Status queries
CREATE INDEX idx_npcs_status ON npcs(status);
CREATE INDEX idx_campaigns_active ON campaigns(is_active);
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DB_URL)

def init_scalable_schema():
    """
    Initialize proper scalable schema in the main agentic_dnd database
    
    Architecture:
    - One database holds everything
    - Isolation through campaign_id foreign keys
    - Proper indexing for performance
    - Ready for thousands of users/campaigns
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("🏗️ Creating scalable database schema in agentic_dnd...")
    
    # Execute the schema SQL
    cur.execute(SCHEMA_SQL)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ Scalable schema created successfully!")
    print("\n🎯 Key Features:")
    print("   → Campaign isolation via UUID foreign keys")
    print("   → Optimized indexes for fast queries") 
    print("   → Ready for thousands of users")
    print("   → Clean data separation")
    print("   → Production-ready architecture")

if __name__ == "__main__":
    init_scalable_schema() 