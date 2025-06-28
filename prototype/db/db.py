import os
import psycopg2

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

