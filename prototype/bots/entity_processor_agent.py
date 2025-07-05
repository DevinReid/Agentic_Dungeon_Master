#!/usr/bin/env python3
"""
Entity Processor Agent

Transforms raw extracted entities into complete, database-ready records using batch processing.
Handles duplicate resolution, entity individualization, and full stat/lore generation in one AI call.
Saves directly to PostgreSQL and vectorizer, bypassing ContentProcessor.
"""

import json
import uuid
from typing import List, Dict, Any, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv
import psycopg2.extras

load_dotenv()

class EntityProcessorAgent:
    """
    Batch entity processor that resolves duplicates and generates complete entity records in one AI call
    """
    
    def __init__(self, debug=False):
        self.debug = debug
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if self.debug:
            print("🔄 EntityProcessorAgent initialized")
    
    def process_entities(self, raw_entities: List[Dict[str, Any]], campaign_id: str, 
                        content: str, content_type: str, world_id: str = None, 
                        save_direct: bool = True, source_content_id: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Main processing method that transforms raw entities into database-ready records
        
        Args:
            raw_entities: Raw entities from EntityExtractorAgent
            campaign_id: Campaign UUID for context
            content: Original content for context
            content_type: Type of content being processed
            world_id: World UUID for direct saves (optional)
            save_direct: If True, save directly to PostgreSQL and vectorizer
            source_content_id: ID of source content for entity linking (optional)
            
        Returns:
            Dict with keys: 'npcs', 'locations', 'organizations', 'artifacts', 'deities', 'threats'
            Each containing lists of complete database records
        """
        if not raw_entities:
            return {'npcs': [], 'locations': [], 'organizations': [], 'artifacts': [], 'deities': [], 'threats': [], 'events': [], 'items': []}
        
        try:
            # Get existing entities context
            existing_context = self._get_existing_entities_context(campaign_id)
            
            # Split entities into batches to avoid token limits
            batch_size = 8  # Process 8 entities at a time to stay well under token limits
            batches = [raw_entities[i:i + batch_size] for i in range(0, len(raw_entities), batch_size)]
            
            # Process each batch and combine results
            combined_results = {'npcs': [], 'locations': [], 'organizations': [], 'artifacts': [], 'deities': [], 'threats': [], 'events': [], 'items': []}
            
            for i, batch in enumerate(batches):
                batch_results = self._batch_process_entities(
                    batch, campaign_id, content, content_type, existing_context
                )
                
                # Combine results
                for entity_type, entities in batch_results.items():
                    combined_results[entity_type].extend(entities)
            
            # DIRECT SAVE TO DATABASE AND VECTORIZER
            if save_direct and world_id:
                self._save_entities_direct(combined_results, campaign_id, world_id, content_type, source_content_id)
                self._vectorize_entities_direct(combined_results, campaign_id, world_id, content_type)
            
            return combined_results
            
        except Exception as e:
            print(f"❌ Batch entity processing failed: {e}")
            # Fallback to empty results
            return {'npcs': [], 'locations': [], 'organizations': [], 'artifacts': [], 'deities': [], 'threats': [], 'events': [], 'items': []}
    
    def _save_entities_direct(self, processed_entities: Dict[str, List[Dict[str, Any]]], 
                             campaign_id: str, world_id: str, content_type: str, source_content_id: str):
        """Save processed entities directly to PostgreSQL database tables"""
        try:
            from db.db import get_db_connection
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            if self.debug:
                print("💾 Saving NPCs directly to npcs table...")
            
            # Save NPCs to dedicated npc table
            for npc in processed_entities.get('npcs', []):
                try:
                    cur.execute("""
                        INSERT INTO npcs (npc_id, campaign_id, name, class, level, hp, max_hp, ac,
                                         strength, dexterity, constitution, intelligence, wisdom, charisma,
                                         status, disposition, backstory, personality_traits, flaws, bonds,
                                         notable_abilities, relationships, lore, tags, source_content_type,
                                         current_location_id, last_seen)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (npc_id) DO NOTHING;
                    """, (
                        npc['npc_id'], campaign_id, npc['name'], npc.get('class'), npc.get('level'),
                        npc.get('hp'), npc.get('max_hp'), npc.get('ac'), npc.get('strength'), 
                        npc.get('dexterity'), npc.get('constitution'), npc.get('intelligence'),
                        npc.get('wisdom'), npc.get('charisma'), npc.get('status'), npc.get('disposition'),
                        npc.get('backstory'),                     npc.get('personality_traits', []),  # PostgreSQL will handle array conversion
                        npc.get('flaws', []), npc.get('bonds', []),
                        npc.get('notable_abilities', []), 
                        psycopg2.extras.Json(npc.get('relationships', [])), npc.get('lore'),
                        npc.get('tags', []), content_type, npc.get('current_location_id'), npc.get('last_seen')
                    ))
                except Exception as e:
                    if self.debug:
                        print(f"⚠️ Failed to save NPC {npc.get('name', 'Unknown')}: {e}")
                    continue
            
            if self.debug:
                print("💾 Saving locations directly to locations table...")
            
            # Save Locations to dedicated locations table
            for location in processed_entities.get('locations', []):
                try:
                    cur.execute("""
                        INSERT INTO locations (location_id, campaign_id, name, description, notable_features,
                                             connections, location_type, size, inhabitants, notable_items,
                                             atmosphere, relationships, lore, tags, source_content_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (location_id) DO NOTHING;
                    """, (
                        location['location_id'], campaign_id, location['name'], location.get('description'),
                        location.get('notable_features'),                     psycopg2.extras.Json(location.get('connections', {})),  # Convert dict to JSON
                        location.get('location_type'), location.get('size'), 
                        location.get('inhabitants', []),  # PostgreSQL will handle array conversion
                        location.get('notable_items', []), location.get('atmosphere'),
                        psycopg2.extras.Json(location.get('relationships', [])), location.get('lore'),
                        location.get('tags', []), content_type
                    ))
                except Exception as e:
                    if self.debug:
                        print(f"⚠️ Failed to save location {location.get('name', 'Unknown')}: {e}")
                    continue
            
            if self.debug:
                print("💾 Saving other entities directly to extracted_entities table...")
            
            # Save other entities (artifacts, organizations, deities, threats, events, items) to extracted_entities
            for entity_type in ['organizations', 'artifacts', 'deities', 'threats', 'events', 'items']:
                for entity in processed_entities.get(entity_type, []):
                    try:
                        # Store additional entity data as JSON in extraction_context temporarily
                        entity_json = json.dumps(entity)
                        
                        cur.execute("""
                            INSERT INTO extracted_entities (entity_id, world_id, campaign_id, source_content_id,
                                                          entity_type, entity_name, description, status, tags, 
                                                          extraction_context)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (entity_id) DO NOTHING;
                        """, (
                            entity['entity_id'], world_id, campaign_id, source_content_id,  # Use source_content_id for linking
                            entity_type[:-1],  # Remove 's' from plural  
                            entity['entity_name'], entity.get('description'), entity.get('status', 'extracted'),
                            entity.get('tags', []), entity_json  # Store full entity as JSON in extraction_context
                        ))
                    except Exception as e:
                        if self.debug:
                            print(f"⚠️ Failed to save {entity_type[:-1]} {entity.get('entity_name', 'Unknown')}: {e}")
                        continue
            
            conn.commit()
            cur.close()
            conn.close()
            
            pass
                
        except Exception as e:
            print(f"❌ Failed to save entities directly: {e}")
            import traceback
            traceback.print_exc()
    
    def _vectorize_entities_direct(self, processed_entities: Dict[str, List[Dict[str, Any]]], 
                                  campaign_id: str, world_id: str, content_type: str):
        """Send processed entities directly to vectorizer"""
        try:
            from services.vector_service import VectorService
            
            vector_service = VectorService(debug=self.debug)
            
            if self.debug:
                print("🔍 Vectorizing entities directly...")
            
            # Vectorize NPCs with rich personality data
            for npc in processed_entities.get('npcs', []):
                npc_text = self._create_npc_vector_text(npc)
                vector_id = f"npc_{npc['npc_id']}"
                
                metadata = {
                    "content_id": npc['npc_id'],
                    "campaign_id": campaign_id,
                    "world_id": world_id,
                    "content_type": "npc_profile",
                    "entity_type": "npc",
                    "entity_name": npc['name'],
                    "tags": npc.get('tags', [])[:10],
                    "text_snippet": npc_text[:500] + "..." if len(npc_text) > 500 else npc_text,
                    "is_entity": True
                }
                
                embedding = vector_service.generate_embedding(npc_text)
                vector_service.index.upsert(vectors=[(vector_id, embedding, metadata)])
            
            # Vectorize Locations with rich descriptive data
            for location in processed_entities.get('locations', []):
                location_text = self._create_location_vector_text(location)
                vector_id = f"location_{location['location_id']}"
                
                metadata = {
                    "content_id": location['location_id'],
                    "campaign_id": campaign_id,
                    "world_id": world_id,
                    "content_type": "location_profile",
                    "entity_type": "location",
                    "entity_name": location['name'],
                    "tags": location.get('tags', [])[:10],
                    "text_snippet": location_text[:500] + "..." if len(location_text) > 500 else location_text,
                    "is_entity": True
                }
                
                embedding = vector_service.generate_embedding(location_text)
                vector_service.index.upsert(vectors=[(vector_id, embedding, metadata)])
            
            # Vectorize other entities
            for entity_type in ['organizations', 'artifacts', 'deities', 'threats', 'events', 'items']:
                for entity in processed_entities.get(entity_type, []):
                    entity_text = self._create_entity_vector_text(entity)
                    vector_id = f"{entity_type[:-1]}_{entity['entity_id']}"  # Remove 's'
                    
                    metadata = {
                        "content_id": entity['entity_id'],
                        "campaign_id": campaign_id,
                        "world_id": world_id,
                        "content_type": f"{entity_type[:-1]}_profile",
                        "entity_type": entity_type[:-1],
                        "entity_name": entity['entity_name'],
                        "tags": entity.get('tags', [])[:10],
                        "text_snippet": entity_text[:500] + "..." if len(entity_text) > 500 else entity_text,
                        "is_entity": True
                    }
                    
                    embedding = vector_service.generate_embedding(entity_text)
                    vector_service.index.upsert(vectors=[(vector_id, embedding, metadata)])
            
            pass
                
        except Exception as e:
            print(f"❌ Failed to vectorize entities directly: {e}")
    
    def _create_npc_vector_text(self, npc: Dict[str, Any]) -> str:
        """Create rich text for NPC vectorization"""
        parts = []
        
        if npc.get('name'):
            parts.append(f"Name: {npc['name']}")
        if npc.get('class'):
            parts.append(f"Class: {npc['class']}")
        if npc.get('backstory'):
            parts.append(f"Background: {npc['backstory']}")
        if npc.get('personality_traits'):
            parts.append(f"Personality: {', '.join(npc['personality_traits'])}")
        if npc.get('lore'):
            parts.append(f"Lore: {npc['lore']}")
        if npc.get('notable_abilities'):
            parts.append(f"Abilities: {', '.join(npc['notable_abilities'])}")
        
        return " | ".join(parts)
    
    def _create_location_vector_text(self, location: Dict[str, Any]) -> str:
        """Create rich text for location vectorization"""
        parts = []
        
        if location.get('name'):
            parts.append(f"Name: {location['name']}")
        if location.get('description'):
            parts.append(f"Description: {location['description']}")
        if location.get('notable_features'):
            parts.append(f"Features: {location['notable_features']}")
        if location.get('atmosphere'):
            parts.append(f"Atmosphere: {location['atmosphere']}")
        if location.get('lore'):
            parts.append(f"Lore: {location['lore']}")
        
        return " | ".join(parts)
    
    def _create_entity_vector_text(self, entity: Dict[str, Any]) -> str:
        """Create rich text for other entity vectorization"""
        parts = []
        
        if entity.get('entity_name'):
            parts.append(f"Name: {entity['entity_name']}")
        if entity.get('description'):
            parts.append(f"Description: {entity['description']}")
        if entity.get('history'):
            parts.append(f"History: {entity['history']}")
        if entity.get('properties'):
            parts.append(f"Properties: {', '.join(entity['properties']) if isinstance(entity['properties'], list) else entity['properties']}")
        
        return " | ".join(parts)
    
    def _batch_process_entities(self, raw_entities: List[Dict[str, Any]], campaign_id: str,
                               content: str, content_type: str, existing_context: str) -> Dict[str, List[Dict[str, Any]]]:
        """Single AI call to process a batch of entities (8 or fewer) with structured format templates"""
        
        # Define JSON format templates for each entity type
        npc_format = {
            "npc_id": "generate a real UUID",
            "campaign_id": "UUID", 
            "name": "Complete NPC Name",
            "class": "Cleric/Fighter/Wizard/Commoner/etc",
            "level": "1-20 based on importance",
            "hp": "appropriate HP for level",
            "max_hp": "same as hp",
            "ac": "appropriate AC (10-20)",
            "strength": "3-20",
            "dexterity": "3-20", 
            "constitution": "3-20",
            "intelligence": "3-20",
            "wisdom": "3-20",
            "charisma": "3-20",
            "status": "alive/dead/fled",
            "disposition": "friendly/hostile/neutral",
            "backstory": "Rich background story",
            "personality_traits": ["trait1", "trait2"],
            "flaws": ["flaw1"],
            "bonds": ["bond1"],
            "notable_abilities": ["special abilities or spells"],
            "relationships": [{"target": "entity_name", "type": "serves/guards/enemy/etc"}],
            "lore": "Additional world lore and history",
            "tags": ["relevant", "tags"]
        }
        
        location_format = {
            "location_id": "generate a real UUID",
            "campaign_id": "UUID",
            "name": "Complete Location Name", 
            "description": "Rich description of the location",
            "notable_features": "Key features for gameplay",
            "connections": {"direction": "connected_location_name"},
            "location_type": "temple/city/dungeon/forest/cave/etc",
            "size": "small/medium/large/massive",
            "inhabitants": ["types of creatures or NPCs"],
            "notable_items": ["important items found here"],
            "atmosphere": "peaceful/ominous/mysterious/bustling",
            "relationships": [{"target": "entity_name", "type": "contains/near/connected_to"}],
            "lore": "Historical significance and world lore",
            "tags": ["relevant", "tags"]
        }
        
        artifact_format = {
            "entity_id": "generate a real UUID",
            "campaign_id": "UUID",
            "entity_type": "artifact",
            "entity_name": "Artifact Name",
            "description": "Detailed description",
            "artifact_type": "weapon/armor/wondrous_item/etc",
            "rarity": "common/uncommon/rare/very_rare/legendary",
            "properties": ["magical properties"],
            "requirements": "usage requirements if any",
            "history": "origin story and past owners", 
            "relationships": [{"target": "entity_name", "type": "created_by/owned_by/etc"}],
            "status": "extracted",
            "tags": ["relevant", "tags"]
        }
        
        organization_format = {
            "entity_id": "generate a real UUID", 
            "campaign_id": "UUID",
            "entity_type": "organization",
            "entity_name": "Organization Name",
            "description": "Purpose and activities",
            "organization_type": "religious/political/military/guild/etc",
            "size": "small/medium/large/massive",
            "influence": "local/regional/continental/global",
            "structure": "hierarchy and leadership",
            "goals": ["primary objectives"],
            "notable_members": ["key NPCs in the organization"],
            "relationships": [{"target": "entity_name", "type": "allied_with/opposes/etc"}],
            "status": "extracted",
            "tags": ["relevant", "tags"]
        }
        
        # Simple quote escaping to avoid JSON parsing issues
        escaped_content = content.replace('"', "'").replace('\n', ' ').replace('\r', '')
        
        prompt = f"""You are processing extracted D&D entities into complete, database-ready records. 

TASK: Transform raw entities into complete records with full details, resolve duplicates, individuate generics, and establish relationships.

RAW ENTITIES TO PROCESS: {json.dumps(raw_entities, indent=2)}

EXISTING CAMPAIGN CONTEXT: {existing_context}

ORIGINAL CONTENT: {escaped_content}

PROCESSING RULES:
1. MERGE DUPLICATES: "High Priest of Lora" + "Melphis Actar" → One complete NPC  
2. INDIVIDUATE GENERICS: "two goblins" → Two unique NPCs with names, roles, personalities
3. ESTABLISH RELATIONSHIPS: Connect entities mentioned together (guards, serves, located_in, etc.)
4. ADD TEMPORAL CONTEXT: "recently destroyed" → "destroyed 2 weeks ago"
5. GENERATE COMPLETE RECORDS: Full stats for NPCs, rich descriptions for locations

Use the following format for each entity type:

NPC: {json.dumps(npc_format, indent=2)}

LOCATION: {json.dumps(location_format, indent=2)}

ARTIFACT: {json.dumps(artifact_format, indent=2)}

ORGANIZATION: {json.dumps(organization_format, indent=2)}

FOR OTHER TYPES (deity, threat, event, item): Use artifact_format but change entity_type accordingly.

Return JSON with this structure:
{{
  "npcs": [list of complete NPC records],
  "locations": [list of complete location records], 
  "artifacts": [list of artifact records],
  "organizations": [list of organization records],
  "deities": [list of deity records],
  "threats": [list of threat records],
  "events": [list of event records],
  "items": [list of item records]
}}

CRITICAL: Generate REAL UUIDs (like '550e8400-e29b-41d4-a716-446655440000') for all _id fields, maintain relationships between entities, ensure rich detail for gameplay use."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o which supports structured output
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4000,  # High limit for complete records; batching keeps us under this
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            
            # Add missing campaign_id and generate UUIDs if needed
            processed_result = self._ensure_database_fields(result, campaign_id, content_type)
            
            return processed_result
            
        except Exception as e:
            if self.debug:
                print(f"❌ Batch AI processing failed: {e}")
            raise
    
    def _ensure_database_fields(self, result: Dict, campaign_id: str, content_type: str) -> Dict[str, List[Dict[str, Any]]]:
        """Ensure all entities have required database fields"""
        
        processed_result = {
            'npcs': [],
            'locations': [], 
            'organizations': [],
            'artifacts': [],
            'deities': [],
            'threats': [],
            'events': [],
            'items': []
        }
        
        for entity_type, entities in result.items():
            if not isinstance(entities, list):
                continue
                
            for entity in entities:
                if not isinstance(entity, dict):
                    continue
                
                # Ensure required fields
                if entity_type == 'npcs':
                    # Validate and fix UUID if needed
                    if 'npc_id' not in entity or not entity['npc_id'] or not self._is_valid_uuid(entity['npc_id']):
                        entity['npc_id'] = str(uuid.uuid4())
                    entity['campaign_id'] = campaign_id
                    entity['current_location_id'] = None
                    entity['last_seen'] = None
                    entity['source_content_type'] = content_type
                    
                elif entity_type == 'locations':
                    # Validate and fix UUID if needed
                    if 'location_id' not in entity or not entity['location_id'] or not self._is_valid_uuid(entity['location_id']):
                        entity['location_id'] = str(uuid.uuid4()) 
                    entity['campaign_id'] = campaign_id
                    entity['source_content_type'] = content_type
                    
                else:  # artifacts, organizations, deities, threats, events, items
                    # Validate and fix UUID if needed
                    if 'entity_id' not in entity or not entity['entity_id'] or not self._is_valid_uuid(entity['entity_id']):
                        entity['entity_id'] = str(uuid.uuid4())
                    entity['campaign_id'] = campaign_id
                    entity['source_content_type'] = content_type
                    if 'status' not in entity:
                        entity['status'] = 'extracted'
                
                processed_result[entity_type].append(entity)
        
        return processed_result
    
    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """Check if a string is a valid UUID"""
        try:
            uuid.UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False
    
    def _get_existing_entities_context(self, campaign_id: str) -> str:
        """Get context of existing entities for duplicate detection and relationship building"""
        try:
            from db.db import get_db_connection
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get recent entities for context
            cur.execute("""
                (SELECT 'npc' as type, name as entity_name, backstory as description 
                 FROM npcs WHERE campaign_id = %s ORDER BY created_at DESC LIMIT 5)
                UNION ALL
                (SELECT 'location' as type, name as entity_name, description 
                 FROM locations WHERE campaign_id = %s ORDER BY created_at DESC LIMIT 5)
                UNION ALL  
                (SELECT entity_type as type, entity_name, description
                 FROM extracted_entities WHERE campaign_id = %s ORDER BY created_at DESC LIMIT 10)
            """, (campaign_id, campaign_id, campaign_id))
            
            existing = cur.fetchall()
            cur.close()
            conn.close()
            
            if not existing:
                return "No existing entities found - this is a new campaign."
            
            context_lines = []
            for entity_type, name, desc in existing:
                short_desc = (desc or "")[:100] + "..." if desc and len(desc) > 100 else (desc or "")
                context_lines.append(f"{entity_type}: {name} - {short_desc}")
            
            return "\n".join(context_lines)
            
        except Exception as e:
            if self.debug:
                print(f"⚠️ Could not get existing entities context: {e}")
            return "Could not retrieve existing entities context." 