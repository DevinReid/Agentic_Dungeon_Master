#!/usr/bin/env python3
"""
Entity Extractor Agent

AI-powered entity extraction that finds NPCs, locations, organizations, and artifacts
from narrative world content and assigns consistent tags for cross-referencing.
"""
# ! ADD SOME KIND OF DOUBLE CHECK TO MAKE SURE THE ENTITIES ARE NOT ALREADY IN THE DATABASE - This will liekly come from out postgress pull issue
import json
from typing import List, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class EntityExtractorAgent:
    

    def __init__(self, debug=False):
        self.debug = debug
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if self.debug:
            print("🔍 EntityExtractorAgent initialized")
    
    def extract_entities(self, content: str, content_type: str, existing_tags: List[str], 
                        campaign_id: str, world_id: str = None, save_direct: bool = False,
                        source_content_id: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract and process entities into complete database-ready records
        
        Args:
            content: The narrative text content
            content_type: Type of content being processed  
            existing_tags: Tags from content for consistency
            campaign_id: Campaign UUID for context
            world_id: World UUID for direct saves (optional)
            save_direct: If True, EntityProcessor will save directly to PostgreSQL
            source_content_id: ID of source content for entity linking (optional)
            
        Returns:
            Dict with processed entities grouped by type, ready for database insertion
        """
        
        try:
            # Pass 1: Extract raw entities using existing method
            existing_entities = self._get_existing_entities(campaign_id)
            raw_entities = self._ai_extract_entities(content, content_type, existing_tags, existing_entities)
            
            if not raw_entities:
                if self.debug:
                    print("⚠️ No entities extracted")
                return {'npcs': [], 'locations': [], 'organizations': [], 'artifacts': [], 'deities': [], 'threats': [], 'events': [], 'items': []}
            
            # Pass 2: Batch process into complete database records
            from .entity_processor_agent import EntityProcessorAgent
            processor = EntityProcessorAgent(debug=self.debug)
            processed_entities = processor.process_entities(
                raw_entities=raw_entities, 
                campaign_id=campaign_id, 
                content=content, 
                content_type=content_type,
                world_id=world_id,
                save_direct=save_direct,
                source_content_id=source_content_id
            )
            
            if self.debug:
                total_entities = sum(len(entities) for entities in processed_entities.values())
                print(f"✅ Generated {total_entities} complete entity records")
                for entity_type, entities in processed_entities.items():
                    if entities:
                        print(f"   - {len(entities)} {entity_type}")
            
            return processed_entities
            
        except Exception as e:
            print(f"❌ Entity extraction and processing failed: {e}")
            return {'npcs': [], 'locations': [], 'organizations': [], 'artifacts': [], 'deities': [], 'threats': [], 'events': [], 'items': []}
    
    def _ai_extract_entities(self, content: str, content_type: str, existing_tags: List[str], 
                            existing_entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        # Use AI to extract entities from content
        
        # Format existing entities for context
        entity_context = self._format_entity_context(existing_entities)
        
        # Simple quote escaping to avoid JSON parsing issues
        escaped_content = content.replace('"', "'").replace('\n', ' ').replace('\r', '')
        
        prompt = f"""You are an expert at extracting game entities from D&D world building content.

                                CONTENT TYPE: {content_type}
                                CONTENT TO ANALYZE: {escaped_content}

                                EXISTING CONTENT TAGS: {', '.join(existing_tags)}

                                EXISTING ENTITIES IN THIS CAMPAIGN:
                                {entity_context}

                                EXTRACTION RULES:
                                1. Extract entities that could become game objects (NPCs, locations, organizations, artifacts, deities)
                                2. Use existing entity names when referring to the same entities
                                3. Don't extract vague concepts - only concrete entities
                                4. Include enough context to understand what the entity is
                                5. Suggest tags that connect to the content tags: {existing_tags}

                                ENTITY TYPES TO EXTRACT:
                                - npc: Named characters (High Priest Aldric, Queen Soranna)
                                - location: Specific places (Temple of Solara, Crystal Peak, Malakar's Lair)
                                - organization: Groups/factions (Church of Solara, Order of the Dawn)
                                - artifact: Magical items/relics (Crown of Malakar, Sunblade of Dawn)
                                - item: normal items a player might find in the world (potion of healing, scroll of magic missile, iron sword, silver plate, etc.)
                                - deity: Gods/divine beings (Solara, Lunaris, Malakar)
                                - threat: Specific dangers (The Dread Titan, Shadow Plague)
                                - event: Specific events (The Battle of the Crystal Peak, The Great Council of the Gods)

                                For each entity, provide:
                                - entity_name: Proper name
                                - entity_type: One of the types above
                                - description: Brief description from context
                                - extraction_context: The sentence where you found it
                                - suggested_tags: Tags that connect this entity to the content

                                Return ONLY a JSON object:
                                {{
                                "entities": [
                                    {{
                                    "entity_name": "High Priest Aldric",
                                    "entity_type": "npc", 
                                    "description": "Leader of Solara's clergy who teaches healing magic",
                                    "extraction_context": "The High Priest Aldric teaches healing magic to worthy disciples",
                                    "suggested_tags": ["solara", "priest", "healer", "temple", "divine_magic"]
                                    }}
                                ]
                                }}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o which supports structured output
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000,  # High limit to ensure complete JSON. If we hit this, implement content chunking.
                response_format={"type": "json_object"}
            )
            
            # Capture raw response for debug output
            self._last_raw_response = {
                'model': response.model,
                'usage': response.usage.dict() if response.usage else None,
                'choices': [choice.dict() for choice in response.choices],
                'raw_content': response.choices[0].message.content.strip()
            }
            
            result = json.loads(response.choices[0].message.content.strip())
            return result.get('entities', [])
            
        except Exception as e:
            if self.debug:
                print(f"❌ AI entity extraction failed: {e}")
            return []
    
    def _get_existing_entities(self, campaign_id: str) -> Dict[str, List[str]]:
        """Get existing entities from database for consistency"""
        # ? could be moved to db.db
        try:
            from db.db import get_db_connection
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get existing entities by type
            cur.execute("""
                SELECT entity_type, entity_name, description
                FROM extracted_entities 
                WHERE campaign_id = %s
                ORDER BY entity_type, entity_name
            """, (campaign_id,))
            
            entity_data = cur.fetchall()
            cur.close()
            conn.close()
            
            # Organize by type
            entities = {
                'npc': [],
                'location': [],
                'organization': [],
                'artifact': [],
                'deity': [],
                'threat': []
            }
            
            for entity_type, name, description in entity_data:
                if entity_type in entities:
                    entities[entity_type].append(f"{name}: {description}")
                else:
                    entities['npc'].append(f"{name}: {description}")  # Default fallback
            
            return entities
            
        except Exception as e:
            if self.debug:
                print(f"⚠️ Could not get existing entities: {e}")
            return {'npc': [], 'location': [], 'organization': [], 'artifact': [], 'deity': [], 'threat': []}
    
    def _format_entity_context(self, entities: Dict[str, List[str]]) -> str:
        """Format existing entities for AI prompt context"""
        
        context_parts = []
        
        for entity_type, entity_list in entities.items():
            if entity_list:
                context_parts.append(f"{entity_type.upper()}S: {', '.join(entity_list)}")
        
        return "\n".join(context_parts) if context_parts else "No existing entities found - create initial entity vocabulary."
    

 