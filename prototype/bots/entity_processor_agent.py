#!/usr/bin/env python3
"""
Entity Processor Agent

Transforms raw extracted entities into complete, database-ready records using batch processing.
Handles duplicate resolution, entity individualization, and full stat/lore generation in one AI call.
"""

import json
import uuid
from typing import List, Dict, Any, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

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
                        content: str, content_type: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Main processing method that transforms raw entities into database-ready records
        
        Args:
            raw_entities: Raw entities from EntityExtractorAgent
            campaign_id: Campaign UUID for context
            content: Original content for context
            content_type: Type of content being processed
            
        Returns:
            Dict with keys: 'npcs', 'locations', 'organizations', 'artifacts', 'deities', 'threats'
            Each containing lists of complete database records
        """
        if self.debug:
            print(f"🔄 Processing {len(raw_entities)} raw entities with batching")
        
        if not raw_entities:
            return {'npcs': [], 'locations': [], 'organizations': [], 'artifacts': [], 'deities': [], 'threats': [], 'events': [], 'items': []}
        
        try:
            # Get existing entities context
            existing_context = self._get_existing_entities_context(campaign_id)
            
            # Split entities into batches to avoid token limits
            batch_size = 8  # Process 8 entities at a time to stay well under token limits
            batches = [raw_entities[i:i + batch_size] for i in range(0, len(raw_entities), batch_size)]
            
            if self.debug:
                print(f"🔄 Split into {len(batches)} batches of up to {batch_size} entities each")
            
            # Process each batch and combine results
            combined_results = {'npcs': [], 'locations': [], 'organizations': [], 'artifacts': [], 'deities': [], 'threats': [], 'events': [], 'items': []}
            
            for i, batch in enumerate(batches):
                if self.debug:
                    print(f"🔄 Processing batch {i+1}/{len(batches)} ({len(batch)} entities)")
                
                batch_results = self._batch_process_entities(
                    batch, campaign_id, content, content_type, existing_context
                )
                
                # Combine results
                for entity_type, entities in batch_results.items():
                    combined_results[entity_type].extend(entities)
            
            if self.debug:
                total_entities = sum(len(entities) for entities in combined_results.values())
                print(f"✅ Generated {total_entities} complete entity records across {len(batches)} batches")
            
            return combined_results
            
        except Exception as e:
            print(f"❌ Batch entity processing failed: {e}")
            # Fallback to empty results
            return {'npcs': [], 'locations': [], 'organizations': [], 'artifacts': [], 'deities': [], 'threats': [], 'events': [], 'items': []}
    
    def _batch_process_entities(self, raw_entities: List[Dict[str, Any]], campaign_id: str,
                               content: str, content_type: str, existing_context: str) -> Dict[str, List[Dict[str, Any]]]:
        """Single AI call to process a batch of entities (8 or fewer) with structured format templates"""
        
        # Define JSON format templates for each entity type
        npc_format = {
            "npc_id": "UUID (generated)",
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
            "location_id": "UUID (generated)",
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
            "entity_id": "UUID (generated)",
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
            "entity_id": "UUID (generated)", 
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

CRITICAL: Generate UUIDs for all _id fields, maintain relationships between entities, ensure rich detail for gameplay use."""

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
                    if 'npc_id' not in entity or not entity['npc_id']:
                        entity['npc_id'] = str(uuid.uuid4())
                    entity['campaign_id'] = campaign_id
                    entity['current_location_id'] = None
                    entity['last_seen'] = None
                    entity['source_content_type'] = content_type
                    
                elif entity_type == 'locations':
                    if 'location_id' not in entity or not entity['location_id']:
                        entity['location_id'] = str(uuid.uuid4()) 
                    entity['campaign_id'] = campaign_id
                    entity['source_content_type'] = content_type
                    
                else:  # artifacts, organizations, deities, threats, events, items
                    if 'entity_id' not in entity or not entity['entity_id']:
                        entity['entity_id'] = str(uuid.uuid4())
                    entity['campaign_id'] = campaign_id
                    entity['source_content_type'] = content_type
                    if 'status' not in entity:
                        entity['status'] = 'extracted'
                
                processed_result[entity_type].append(entity)
        
        return processed_result
    
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