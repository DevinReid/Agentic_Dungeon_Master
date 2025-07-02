#!/usr/bin/env python3
"""
Proper scalable database schema for the Agentic D&D system

This creates all tables in ONE database with proper campaign_id isolation.
Ready for thousands of users and campaigns.
"""

import os
import psycopg2
from dotenv import load_dotenv


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
    tags TEXT[] DEFAULT '{}',      -- AI-generated tags ['temple', 'solara', 'holy_ground', 'mountain_peak']
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
    tags TEXT[] DEFAULT '{}',      -- AI-generated tags ['solara', 'priest', 'spell_teacher', 'friendly']
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

-- ========================================
-- WORLD BUILDING TABLES
-- ========================================
-- These tables store AI-generated world content for campaigns
-- Generated by UniverseBuilder, RegionalBuilder, etc.

-- 9. WORLDS - Basic world metadata and campaign linkage
CREATE TABLE worlds (
    world_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    world_name TEXT NOT NULL,
    scope TEXT NOT NULL,           -- 'intimate', 'regional', 'continental', 'planetary'
    theme_list TEXT,               -- 'magic, adventure, political intrigue'
    region_count INTEGER DEFAULT 1,
    major_city_count INTEGER DEFAULT 1, 
    settlement_count INTEGER DEFAULT 3,
    magic_level TEXT DEFAULT 'medium', -- 'none', 'low', 'medium', 'high'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id) -- One world per campaign
);

-- 10. WORLD_CONTENT - Rich narrative content + structured JSON metadata
CREATE TABLE world_content (
    content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_content_id UUID REFERENCES world_content(content_id), -- For hierarchical content (expansions)
    world_id UUID REFERENCES worlds(world_id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,     -- 'universe_builder', 'expansion_bot', 'regional_builder', 'manual'
    content_type TEXT NOT NULL,    -- 'world_overview', 'magic_system', 'pantheon', 'global_threats', 'political_structure', 'regional_overview'
    title TEXT NOT NULL,
    content TEXT NOT NULL,         -- The full paragraph/essay content
    metadata JSONB,                -- Structured data (UniverseBuilder JSON objects)
    tags TEXT[] DEFAULT '{}',      -- AI-generated tags for cross-referencing ['pantheon', 'solara', 'divine_magic']
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. EXTRACTED_ENTITIES - NPCs, places, artifacts mentioned in world content
CREATE TABLE extracted_entities (
    entity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(world_id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    source_content_id UUID REFERENCES world_content(content_id), -- Where it was extracted from
    entity_type TEXT NOT NULL,     -- 'npc', 'location', 'organization', 'artifact', 'deity', 'threat'
    entity_name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'extracted', -- 'extracted', 'generated', 'detailed'
    tags TEXT[] DEFAULT '{}',      -- AI-generated tags ['solara', 'priest', 'spell_teacher', 'temple_of_solara']
    game_object_id UUID,           -- Links to actual NPC/location table when created
    extraction_context TEXT,       -- The sentence it was extracted from
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. CONTENT_EMBEDDINGS - Vector embeddings for semantic search (requires pgvector extension)
-- TODO: Uncomment when pgvector extension is installed
/*
CREATE TABLE content_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(world_id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    source_content_id UUID REFERENCES world_content(content_id), -- Original essay
    snippet_text TEXT NOT NULL,    -- "Lord Vanderlay lives on a hill in the arakus forest"
    embedding vector(1536),        -- The actual vector (requires pgvector extension)
    snippet_type TEXT DEFAULT 'fact', -- 'fact', 'relationship', 'description', 'conflict'
    entities_mentioned TEXT[],     -- ['Lord Vanderlay', 'Arakus Forest'] for easy filtering
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
*/

-- INDEXES FOR WORLD BUILDING TABLES
CREATE INDEX idx_worlds_campaign ON worlds(campaign_id);
CREATE INDEX idx_world_content_world ON world_content(world_id);
CREATE INDEX idx_world_content_campaign ON world_content(campaign_id);
CREATE INDEX idx_world_content_type ON world_content(content_type);
CREATE INDEX idx_extracted_entities_world ON extracted_entities(world_id);
CREATE INDEX idx_extracted_entities_campaign ON extracted_entities(campaign_id);
CREATE INDEX idx_extracted_entities_type ON extracted_entities(entity_type);

-- GIN INDEXES FOR TAG ARRAY SEARCHING (Fast "tag IN array" queries)
CREATE INDEX idx_world_content_tags ON world_content USING GIN (tags);
CREATE INDEX idx_extracted_entities_tags ON extracted_entities USING GIN (tags);
CREATE INDEX idx_npcs_tags ON npcs USING GIN (tags);
CREATE INDEX idx_locations_tags ON locations USING GIN (tags);
-- TODO: Uncomment when pgvector extension is installed
-- CREATE INDEX idx_content_embeddings_world ON content_embeddings(world_id);
-- CREATE INDEX idx_content_embeddings_campaign ON content_embeddings(campaign_id);

-- 13. TAG_VOCABULARY - Track tag usage patterns for AI consistency
CREATE TABLE tag_vocabulary (
    tag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    tag_name TEXT NOT NULL,
    tag_category TEXT,             -- 'entity', 'theme', 'category', 'location', 'relationship'
    usage_count INTEGER DEFAULT 1,
    first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, tag_name)  -- One tag per campaign (but different campaigns can have same tag)
);

CREATE INDEX idx_tag_vocabulary_campaign ON tag_vocabulary(campaign_id);
CREATE INDEX idx_tag_vocabulary_category ON tag_vocabulary(tag_category);
CREATE INDEX idx_tag_vocabulary_usage ON tag_vocabulary(usage_count DESC);

-- ========================================
-- USER FLOW NOTES FOR CAMPAIGN + WORLD
-- ========================================
-- Planned User Flow:
-- 1. User clicks "Start New Campaign"
-- 2. System asks: "Create new world or use existing world?"
-- 3. If new world: Run UniverseBuilder → Save to world_content table
-- 4. Campaign begins with world_context

-- Database Relationships:
-- campaigns.campaign_id → world_content.campaign_id (one-to-many)
-- world_content.content_id → extracted_entities.source_content_id (one-to-many)  
-- world_content.content_id → content_embeddings.source_content_id (one-to-many)
-- extracted_entities.game_object_id → npcs.npc_id | locations.location_id (when generated)

-- ========================================

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