import os
import psycopg2
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
  # E.g. postgres://user:pass@localhost/dbname

def get_db_connection():
    return psycopg2.connect(DB_URL)

# =============================================================================
# USER MANAGEMENT (for future multiplayer)
# =============================================================================

def create_user(username, email=None):
    """Create a new user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO users (username, email)
        VALUES (%s, %s)
        RETURNING user_id;
    """, (username, email))
    
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return user_id

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT user_id, username, email, created_at, last_login
        FROM users WHERE username = %s;
    """, (username,))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        return {
            "user_id": result[0],
            "username": result[1], 
            "email": result[2],
            "created_at": result[3],
            "last_login": result[4]
        }
    return None

def get_or_create_user(username):
    """Get existing user or create new one (for single player simplicity)"""
    user = get_user_by_username(username)
    if user:
        return user["user_id"]
    else:
        return create_user(username)

# =============================================================================
# CAMPAIGN MANAGEMENT
# =============================================================================

def create_campaign(name, description, created_by_user_id):
    """Create a new campaign"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO campaigns (name, description, created_by)
        VALUES (%s, %s, %s)
        RETURNING campaign_id;
    """, (name, description, created_by_user_id))
    
    campaign_id = cur.fetchone()[0]
    
    # Add creator as a member with 'dm' role
    cur.execute("""
        INSERT INTO campaign_members (campaign_id, user_id, role)
        VALUES (%s, %s, 'dm');
    """, (campaign_id, created_by_user_id))

    conn.commit()
    cur.close()
    conn.close()

    return campaign_id

def list_campaigns(user_id=None):
    """List all campaigns, optionally filtered by user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if user_id:
        # Get campaigns the user has access to
        cur.execute("""
            SELECT c.campaign_id, c.name, c.description, c.created_at, c.last_played,
                   u.username as creator, cm.role
            FROM campaigns c
            JOIN campaign_members cm ON c.campaign_id = cm.campaign_id
            JOIN users u ON c.created_by = u.user_id
            WHERE cm.user_id = %s AND c.is_active = true
            ORDER BY c.last_played DESC;
        """, (user_id,))
    else:
        # Get all active campaigns
        cur.execute("""
            SELECT c.campaign_id, c.name, c.description, c.created_at, c.last_played,
                   u.username as creator
            FROM campaigns c
            JOIN users u ON c.created_by = u.user_id
            WHERE c.is_active = true
            ORDER BY c.last_played DESC;
        """)
    
    campaigns = cur.fetchall()
    cur.close()
    conn.close()
    
    return campaigns

def get_most_recent_campaign(user_id):
    """Get the most recently played campaign for a user"""
    campaigns = list_campaigns(user_id)
    return campaigns[0] if campaigns else None

def update_campaign_last_played(campaign_id):
    """Update when campaign was last played"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE campaigns 
        SET last_played = CURRENT_TIMESTAMP 
        WHERE campaign_id = %s;
    """, (campaign_id,))
    
    conn.commit()
    cur.close()
    conn.close()

# =============================================================================
# CHARACTER MANAGEMENT
# =============================================================================

def create_character(campaign_id, user_id, name, char_class, hp=30):
    """Create a character in a campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO characters (campaign_id, user_id, name, class, hp, max_hp)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING character_id;
    """, (campaign_id, user_id, name, char_class, hp, hp))
    
    character_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return character_id

def get_character_in_campaign(campaign_id, user_id):
    """Get user's character in a specific campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT character_id, name, class, level, hp, max_hp, ac,
               strength, dexterity, constitution, intelligence, wisdom, charisma, experience
        FROM characters 
        WHERE campaign_id = %s AND user_id = %s;
    """, (campaign_id, user_id))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        return {
            "character_id": result[0], "name": result[1], "class": result[2],
            "level": result[3], "hp": result[4], "max_hp": result[5], "ac": result[6],
            "strength": result[7], "dexterity": result[8], "constitution": result[9],
            "intelligence": result[10], "wisdom": result[11], "charisma": result[12],
            "experience": result[13]
        }
    return None

def update_character_stats(character_id, stats):
    """Update character stats"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE characters
        SET strength=%s, dexterity=%s, constitution=%s,
            intelligence=%s, wisdom=%s, charisma=%s,
            level=%s, experience=%s, hp=%s, max_hp=%s, ac=%s
        WHERE character_id=%s;
    """, (
        stats["strength"], stats["dexterity"], stats["constitution"],
        stats["intelligence"], stats["wisdom"], stats["charisma"],
        stats["level"], stats["experience"], stats["hp"], stats["max_hp"], stats["ac"],
        character_id
    ))
    
    conn.commit()
    cur.close()
    conn.close()

def clear_characters_in_campaign(campaign_id):
    """Clear all characters in a campaign (for testing)"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM characters WHERE campaign_id = %s;", (campaign_id,))
    conn.commit()
    cur.close()
    conn.close()

# =============================================================================
# LOCATION MANAGEMENT
# =============================================================================

def create_location(campaign_id, name, description=None):
    """Create a location in a campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO locations (campaign_id, name, description)
        VALUES (%s, %s, %s)
        RETURNING location_id;
    """, (campaign_id, name, description))
    
    location_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return location_id

def get_or_create_location(campaign_id, name, description=None):
    """Get existing location or create new one"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Try to find existing location
    cur.execute("""
        SELECT location_id FROM locations 
        WHERE campaign_id = %s AND name = %s;
    """, (campaign_id, name))
    
    result = cur.fetchone()
    
    if result:
        location_id = result[0]
    else:
        # Create new location
        cur.execute("""
            INSERT INTO locations (campaign_id, name, description)
            VALUES (%s, %s, %s)
            RETURNING location_id;
        """, (campaign_id, name, description))
        
        location_id = cur.fetchone()[0]
        conn.commit()
    
    cur.close()
    conn.close()
    
    return location_id

# =============================================================================
# NPC MANAGEMENT
# =============================================================================

def save_npc(campaign_id, npc_data, location_name="Starting Area"):
    """Save or update an NPC in a campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get or create location
    location_id = get_or_create_location(campaign_id, location_name)
    
    # Check if NPC exists (by name in campaign)
    cur.execute("""
        SELECT npc_id FROM npcs 
        WHERE campaign_id = %s AND name = %s;
    """, (campaign_id, npc_data["name"]))
    
    existing_npc = cur.fetchone()
    
    if existing_npc:
        # Update existing NPC
        npc_id = existing_npc[0]
        cur.execute("""
            UPDATE npcs SET
                hp = %s, max_hp = %s, ac = %s,
                strength = %s, dexterity = %s, constitution = %s,
                intelligence = %s, wisdom = %s, charisma = %s,
                level = %s, current_location_id = %s, status = %s,
                disposition = %s, backstory = %s, last_seen = CURRENT_TIMESTAMP
            WHERE npc_id = %s;
        """, (
            npc_data["hp"], npc_data.get("max_hp", npc_data["hp"]), npc_data["ac"],
            npc_data["strength"], npc_data["dexterity"], npc_data["constitution"],
            npc_data["intelligence"], npc_data["wisdom"], npc_data["charisma"],
            npc_data["level"], location_id, npc_data.get("status", "alive"),
            npc_data.get("disposition", "neutral"), npc_data.get("backstory", ""),
            npc_id
        ))
    else:
        # Create new NPC
        cur.execute("""
            INSERT INTO npcs (campaign_id, name, class, hp, max_hp, ac,
                             strength, dexterity, constitution, intelligence, wisdom, charisma,
                             level, current_location_id, status, disposition, backstory)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING npc_id;
        """, (
            campaign_id, npc_data["name"], npc_data["class"],
            npc_data["hp"], npc_data.get("max_hp", npc_data["hp"]), npc_data["ac"],
            npc_data["strength"], npc_data["dexterity"], npc_data["constitution"],
            npc_data["intelligence"], npc_data["wisdom"], npc_data["charisma"],
            npc_data["level"], location_id, npc_data.get("status", "alive"),
            npc_data.get("disposition", "neutral"), npc_data.get("backstory", "")
        ))
        
        npc_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()
    
    return npc_id

def get_npcs_at_location(campaign_id, location_name, status="alive"):
    """Get all NPCs at a specific location in campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT n.npc_id, n.name, n.class, n.hp, n.max_hp, n.ac,
               n.strength, n.dexterity, n.constitution, n.intelligence, n.wisdom, n.charisma,
               n.level, l.name as location_name, n.status, n.disposition, n.backstory, n.last_seen
        FROM npcs n
        JOIN locations l ON n.current_location_id = l.location_id
        WHERE n.campaign_id = %s AND l.name = %s AND n.status = %s
        ORDER BY n.last_seen DESC;
    """, (campaign_id, location_name, status))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    npcs = []
    for row in results:
        npcs.append({
            "npc_id": row[0], "name": row[1], "class": row[2], "hp": row[3],
            "max_hp": row[4], "ac": row[5], "strength": row[6], "dexterity": row[7],
            "constitution": row[8], "intelligence": row[9], "wisdom": row[10],
            "charisma": row[11], "level": row[12], "current_location": row[13],
            "status": row[14], "disposition": row[15], "backstory": row[16],
            "last_seen": row[17]
        })
    
    return npcs

# =============================================================================
# EVENT MANAGEMENT
# =============================================================================

def save_event(campaign_id, event_type, description, location_name=None, 
               npcs_involved=None, character_ids=None, player_actions=None, 
               consequences=None, session_context=None):
    """Save a story event in a campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    location_id = None
    if location_name:
        location_id = get_or_create_location(campaign_id, location_name)
    
    cur.execute("""
        INSERT INTO events (campaign_id, event_type, description, location_id,
                           npcs_involved, characters_involved, player_actions, 
                           consequences, session_context)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (campaign_id, event_type, description, location_id,
          npcs_involved, character_ids, player_actions, consequences, session_context))
    
    conn.commit()
    cur.close()
    conn.close()

def get_recent_events(campaign_id, limit=10):
    """Get recent events for AI context in campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.event_type, e.description, l.name as location_name, e.npcs_involved,
               e.player_actions, e.consequences, e.created_at
        FROM events e
        LEFT JOIN locations l ON e.location_id = l.location_id
        WHERE e.campaign_id = %s
        ORDER BY e.created_at DESC 
        LIMIT %s;
    """, (campaign_id, limit))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{
        "event_type": row[0], "description": row[1], "location": row[2],
        "npcs_involved": row[3], "player_actions": row[4], 
        "consequences": row[5], "created_at": row[6]
    } for row in results]

# =============================================================================
# RELATIONSHIP MANAGEMENT
# =============================================================================

def update_npc_relationship(campaign_id, npc_name, character_id, relationship_change, interaction_description):
    """Update relationship between NPC and character in campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get NPC ID by name in campaign
    cur.execute("""
        SELECT npc_id FROM npcs WHERE campaign_id = %s AND name = %s;
    """, (campaign_id, npc_name))
    
    npc_result = cur.fetchone()
    if not npc_result:
        cur.close()
        conn.close()
        return  # NPC not found
    
    npc_id = npc_result[0]
    
    # Get current relationship or create new one
    cur.execute("""
        SELECT relationship_score, history FROM relationships 
        WHERE campaign_id = %s AND npc_id = %s AND character_id = %s;
    """, (campaign_id, npc_id, character_id))
    
    result = cur.fetchone()
    
    if result:
        # Update existing relationship
        new_score = max(-100, min(100, result[0] + relationship_change))
        new_history = f"{result[1]}\n{interaction_description}" if result[1] else interaction_description
        
        cur.execute("""
            UPDATE relationships 
            SET relationship_score = %s, history = %s, 
                last_interaction = %s, updated_at = CURRENT_TIMESTAMP
            WHERE campaign_id = %s AND npc_id = %s AND character_id = %s;
        """, (new_score, new_history, interaction_description, campaign_id, npc_id, character_id))
    else:
        # Create new relationship
        relationship_type = "ally" if relationship_change > 0 else "enemy" if relationship_change < 0 else "neutral"
        
        cur.execute("""
            INSERT INTO relationships (campaign_id, character_id, npc_id, relationship_type, 
                                     relationship_score, history, last_interaction)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (campaign_id, character_id, npc_id, relationship_type, 
              relationship_change, interaction_description, interaction_description))
    
    conn.commit()
    cur.close()
    conn.close()

def get_npc_relationships(campaign_id, character_id):
    """Get all NPC relationships for a character in campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT r.npc_id, n.name, r.relationship_type, r.relationship_score, 
               r.history, r.last_interaction, r.updated_at
        FROM relationships r
        JOIN npcs n ON r.npc_id = n.npc_id
        WHERE r.campaign_id = %s AND r.character_id = %s
        ORDER BY r.updated_at DESC;
    """, (campaign_id, character_id))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{
        "npc_id": row[0], "npc_name": row[1], "relationship_type": row[2],
        "relationship_score": row[3], "history": row[4], 
        "last_interaction": row[5], "updated_at": row[6]
    } for row in results]


# =============================================================================
# WORLD BUILDING MANAGEMENT
# =============================================================================

def save_processed_world(campaign_id: str, processed_sections: List[Dict[str, Any]], 
                        world_name: str = None) -> str:
    """
    Save ContentProcessor output to database with full enrichment
    
    Args:
        campaign_id: Campaign UUID
        processed_sections: Output from ContentProcessor.process_universe_content()
        world_name: Optional world name override
        
    Returns:
        world_id: UUID of created world
    """
    import psycopg2.extras
    from services.vector_service import VectorService
    
    if not processed_sections:
        raise ValueError("No processed sections to save")
    
    # Extract world metadata from first section
    first_section = processed_sections[0]
    world_metadata = first_section.get('original_metadata', {})
    
    if not world_name:
        world_name = world_metadata.get('world_name', 'Generated World')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Phase 1: Create world record
        print("💾 Creating world record...")
        scope = world_metadata.get('scope', 'regional')
        theme_list = world_metadata.get('theme_list', '')
        magic_level = world_metadata.get('magic_level', 'medium')
        
        cur.execute("""
            INSERT INTO worlds (campaign_id, world_name, scope, theme_list, 
                               region_count, major_city_count, settlement_count, magic_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING world_id;
        """, (campaign_id, world_name, scope, theme_list, 
              world_metadata.get('region_count', 1),
              world_metadata.get('major_city_count', 1), 
              world_metadata.get('settlement_count', 3),
              magic_level))
        
        world_id = cur.fetchone()[0]
        conn.commit()
        
        # Phase 2: Save each content section with full enrichment
        vector_service = VectorService()
        
        for section in processed_sections:
            print(f"💾 Saving {section['content_type']}...")
            
            # Save main content with tags
            cur.execute("""
                INSERT INTO world_content (world_id, campaign_id, content_type, source_type,
                                         title, content, metadata, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING content_id;
            """, (world_id, campaign_id, section['content_type'], section['source_type'],
                  section['title'], section['narrative_content'],
                  psycopg2.extras.Json(section['original_metadata']),
                  section['tags']))
            
            content_id = cur.fetchone()[0]
            
            # Save extracted entities
            for entity in section['entities']:
                cur.execute("""
                    INSERT INTO extracted_entities (world_id, campaign_id, source_content_id,
                                                  entity_type, entity_name, description, status,
                                                  tags, extraction_context)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (world_id, campaign_id, content_id,
                      entity['entity_type'], entity['entity_name'], entity['description'],
                      entity['status'], entity['tags'], entity.get('extraction_context', '')))
            
            # Create vector embeddings for each chunk
            for chunk in section['chunks']:
                try:
                    vector_service.store_content_chunk_embedding(
                        content_id=str(content_id),
                        campaign_id=str(campaign_id),
                        world_id=str(world_id),
                        chunk_data=chunk
                    )
                except Exception as e:
                    print(f"⚠️ Warning: Vector embedding failed for chunk: {e}")
            
            # Update tag vocabulary
            _update_tag_vocabulary_batch(campaign_id, section['tags'], section['content_type'], cur)
        
        conn.commit()
        print(f"✅ World saved with {len(processed_sections)} sections")
        return str(world_id)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to save processed world: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def save_processed_expansion(campaign_id: str, world_id: str, parent_content_id: str,
                           processed_expansion: Dict[str, Any]) -> str:
    """
    Save expansion content processed by ContentProcessor
    
    Args:
        campaign_id: Campaign UUID
        world_id: World UUID
        parent_content_id: ID of content this expands
        processed_expansion: Output from ContentProcessor.process_expansion_content()
        
    Returns:
        content_id: UUID of created expansion content
    """
    import psycopg2.extras
    from services.vector_service import VectorService
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print(f"💾 Saving expansion for {processed_expansion['content_type']}...")
        
        # Save expansion content
        cur.execute("""
            INSERT INTO world_content (parent_content_id, world_id, campaign_id, 
                                     content_type, source_type, title, content, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING content_id;
        """, (parent_content_id, world_id, campaign_id,
              processed_expansion['content_type'], processed_expansion['source_type'],
              processed_expansion['title'], processed_expansion['narrative_content'],
              processed_expansion['tags']))
        
        expansion_content_id = cur.fetchone()[0]
        
        # Save expansion entities
        for entity in processed_expansion['entities']:
            cur.execute("""
                INSERT INTO extracted_entities (world_id, campaign_id, source_content_id,
                                              entity_type, entity_name, description, status,
                                              tags, extraction_context)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (world_id, campaign_id, expansion_content_id,
                  entity['entity_type'], entity['entity_name'], entity['description'],
                  entity['status'], entity['tags'], entity.get('extraction_context', '')))
        
        # Create vector embeddings for expansion chunks
        vector_service = VectorService()
        for chunk in processed_expansion['chunks']:
            try:
                vector_service.store_content_chunk_embedding(
                    content_id=str(expansion_content_id),
                    campaign_id=str(campaign_id),
                    world_id=str(world_id),
                    chunk_data=chunk
                )
            except Exception as e:
                print(f"⚠️ Warning: Vector embedding failed for expansion chunk: {e}")
        
        # Update tag vocabulary
        _update_tag_vocabulary_batch(campaign_id, processed_expansion['tags'], 
                                   processed_expansion['content_type'], cur)
        
        conn.commit()
        print(f"✅ Expansion saved with {len(processed_expansion['entities'])} entities")
        return str(expansion_content_id)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to save expansion: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def _update_tag_vocabulary_batch(campaign_id: str, tags: List[str], 
                               content_type: str, cursor) -> None:
    """Update tag vocabulary in batch for efficiency"""
    
    for tag in tags:
        # Determine tag category
        if tag in ['pantheon', 'magic_system', 'global_threats', 'world_overview']:
            category = 'category'
        elif tag in ['detailed', 'expanded', 'base']:
            category = 'detail_level'
        elif '_' in tag:
            category = 'theme'
        else:
            category = 'entity'
        
        cursor.execute("""
            INSERT INTO tag_vocabulary (campaign_id, tag_name, tag_category, usage_count)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT (campaign_id, tag_name)
            DO UPDATE SET 
                usage_count = tag_vocabulary.usage_count + 1,
                last_used = CURRENT_TIMESTAMP
        """, (campaign_id, tag, category))

def save_world(campaign_id, world_data):
    """Save world metadata and structured content to database
    
    Args:
        campaign_id: UUID of the campaign
        world_data: Dictionary containing UniverseBuilder JSON output
        
    Returns:
        world_id: UUID of the created world
    """
    
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Extract basic world info
    world_info = world_data.get('world_info', {})
    magic_system = world_data.get('magic_system', {})
    size_info = world_data.get('size', {})
    
    world_name = world_info.get('world_name', 'Unnamed World')
    scope = size_info.get('scope', 'regional')
    theme_list = world_info.get('theme_list', '')
    region_count = size_info.get('region_count', 1)
    major_city_count = size_info.get('major_city_count', 1)
    settlement_count = size_info.get('settlement_count', 3)
    magic_level = magic_system.get('magic_level', 'medium')
    
    # Create the world record
    cur.execute("""
        INSERT INTO worlds (campaign_id, world_name, scope, theme_list, 
                           region_count, major_city_count, settlement_count, magic_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING world_id;
    """, (campaign_id, world_name, scope, theme_list, 
          region_count, major_city_count, settlement_count, magic_level))
    
    world_id = cur.fetchone()[0]
    
    # Commit the world record first so it's available for foreign key references
    conn.commit()
    cur.close()
    conn.close()
    
    # Save structured content for each major section
    content_sections = [
        ('world_info', world_info.get('world_description', ''), world_data.get('world_info')),
        ('magic_system', magic_system.get('mechanics', ''), world_data.get('magic_system')),
        ('pantheon', world_data.get('pantheon', {}).get('structure', ''), world_data.get('pantheon')),
    ]
    
    # Save global threats as separate content entries
    for threat in world_data.get('global_threats', []):
        threat_title = threat.get('primary_threat', 'Unknown Threat')
        threat_content = threat.get('threat_details', '')
        content_sections.append(('global_threat', threat_content, threat))
    
    # Insert all content sections (each creates its own transaction)
    for content_type, content_text, metadata in content_sections:
        if content_text:  # Only save if there's actual content
            save_world_content(world_id, campaign_id, content_type, content_text, metadata)
    
    return world_id

def save_world_content(world_id, campaign_id, content_type, content_text, metadata=None, title=None, create_embedding=True):
    """Save a piece of world content to the database and optionally create embeddings
    
    Args:
        world_id: UUID of the world
        campaign_id: UUID of the campaign
        content_type: Type of content ('world_info', 'magic_system', 'pantheon', 'global_threat', etc.)
        content_text: The narrative text content
        metadata: Optional structured data (JSON object)
        title: Optional title (will generate from content_type if not provided)
        create_embedding: Whether to create vector embeddings (default True)
        
    Returns:
        content_id: UUID of the created content
    """
    import psycopg2.extras
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if not title:
        title = content_type.replace('_', ' ').title()
    
    cur.execute("""
        INSERT INTO world_content (world_id, campaign_id, content_type, source_type, 
                                 title, content, metadata)
        VALUES (%s, %s, %s, 'universe_builder', %s, %s, %s)
        RETURNING content_id;
    """, (world_id, campaign_id, content_type, title, content_text, 
          psycopg2.extras.Json(metadata) if metadata else None))
    
    content_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Create vector embedding if requested and content is substantial
    if create_embedding and content_text and len(content_text.strip()) > 50:
        try:
            from services.vector_service import VectorService
            vector_service = VectorService()
            vector_service.store_world_content_embedding(
                content_id=str(content_id),
                campaign_id=str(campaign_id),
                world_id=str(world_id),
                content_type=content_type,
                title=title,
                text=content_text
            )
        except Exception as e:
            print(f"⚠️ Warning: Content saved to database but vector embedding failed: {e}")
            print("💾 Content is still searchable via regular database queries")
    
    return content_id

def get_world_by_campaign(campaign_id):
    """Get world data for a campaign
    
    Args:
        campaign_id: UUID of the campaign
        
    Returns:
        Dictionary with world metadata and content, or None if no world exists
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get basic world info
    cur.execute("""
        SELECT world_id, world_name, scope, theme_list, region_count, 
               major_city_count, settlement_count, magic_level, created_at
        FROM worlds 
        WHERE campaign_id = %s;
    """, (campaign_id,))
    
    world_row = cur.fetchone()
    if not world_row:
        cur.close()
        conn.close()
        return None
    
    world_data = {
        "world_id": world_row[0],
        "world_name": world_row[1],
        "scope": world_row[2],
        "theme_list": world_row[3],
        "region_count": world_row[4],
        "major_city_count": world_row[5],
        "settlement_count": world_row[6],
        "magic_level": world_row[7],
        "created_at": world_row[8],
        "content": {}
    }
    
    # Get all content for this world
    cur.execute("""
        SELECT content_id, content_type, title, content, metadata, created_at
        FROM world_content 
        WHERE world_id = %s
        ORDER BY created_at;
    """, (world_row[0],))
    
    content_rows = cur.fetchall()
    for row in content_rows:
        content_id, content_type, title, content, metadata, created_at = row
        world_data["content"][content_type] = {
            "content_id": content_id,
            "title": title,
            "content": content,
            "metadata": metadata,
            "created_at": created_at
        }
    
    cur.close()
    conn.close()
    
    return world_data

def search_world_content(campaign_id, query, content_types=None, limit=5):
    """Search world content using semantic search via Pinecone
    
    Args:
        campaign_id: UUID of the campaign
        query: The search query text
        content_types: Optional list of content types to filter by
        limit: Maximum number of results to return
        
    Returns:
        List of matching content with full details from database
    """
    try:
        from services.vector_service import VectorService
        
        vector_service = VectorService()
        
        # Perform semantic search in Pinecone
        vector_results = vector_service.semantic_search(
            query=query,
            campaign_id=str(campaign_id),
            content_types=content_types,
            top_k=limit
        )
        
        if not vector_results:
            print(f"🔍 No semantic matches found for: '{query}'")
            return []
        
        # Get full content details from database
        conn = get_db_connection()
        cur = conn.cursor()
        
        enriched_results = []
        for result in vector_results:
            cur.execute("""
                SELECT content_id, title, content, content_type, metadata, created_at
                FROM world_content 
                WHERE content_id = %s;
            """, (result["content_id"],))
            
            db_row = cur.fetchone()
            if db_row:
                enriched_results.append({
                    "content_id": db_row[0],
                    "title": db_row[1],
                    "content": db_row[2],
                    "content_type": db_row[3],
                    "metadata": db_row[4],
                    "created_at": db_row[5],
                    "similarity_score": result["score"],
                    "text_snippet": result["text_snippet"]
                })
        
        cur.close()
        conn.close()
        
        print(f"🎯 Found {len(enriched_results)} semantic matches for: '{query}'")
        return enriched_results
        
    except Exception as e:
        print(f"⚠️ Semantic search failed, falling back to database text search: {e}")
        
        # Fallback to simple database text search
        conn = get_db_connection()
        cur = conn.cursor()
        
        content_type_filter = ""
        params = [str(campaign_id), f"%{query}%"]
        
        if content_types:
            placeholders = ",".join(["%s"] * len(content_types))
            content_type_filter = f"AND content_type IN ({placeholders})"
            params.extend(content_types)
        
        cur.execute(f"""
            SELECT content_id, title, content, content_type, metadata, created_at
            FROM world_content 
            WHERE campaign_id = %s 
            AND (title ILIKE %s OR content ILIKE %s)
            {content_type_filter}
            ORDER BY created_at DESC
            LIMIT %s;
        """, params + [f"%{query}%", limit])
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        fallback_results = []
        for row in results:
            fallback_results.append({
                "content_id": row[0],
                "title": row[1],
                "content": row[2],
                "content_type": row[3],
                "metadata": row[4],
                "created_at": row[5],
                "similarity_score": 0.5,  # Default score for text search
                "text_snippet": row[2][:500] + "..." if len(row[2]) > 500 else row[2]
            })
        
        print(f"🔍 Fallback search found {len(fallback_results)} text matches")
        return fallback_results

