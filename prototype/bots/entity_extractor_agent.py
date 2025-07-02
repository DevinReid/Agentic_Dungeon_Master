#!/usr/bin/env python3
"""
Entity Extractor Agent

AI-powered entity extraction that finds NPCs, locations, organizations, and artifacts
from narrative world content and assigns consistent tags for cross-referencing.
"""

import json
from typing import List, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class EntityExtractorAgent:
    """AI bot that extracts game entities from narrative content"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if self.debug:
            print("🔍 EntityExtractorAgent initialized")
    
    def extract_entities(self, content: str, content_type: str, existing_tags: List[str], 
                        campaign_id: str) -> List[Dict[str, Any]]:
        """
        Extract entities from narrative content with consistent tagging
        
        Args:
            content: The narrative text content
            content_type: Type of content ('pantheon', 'magic_system', etc.)
            existing_tags: Tags already generated for this content
            campaign_id: Campaign UUID for consistency
            
        Returns:
            List of extracted entities with metadata and tags
        """
        if self.debug:
            print(f"🔍 Extracting entities from {content_type}")
        
        try:
            # Get existing entities for consistency
            existing_entities = self._get_existing_entities(campaign_id)
            
            # Extract entities using AI
            entities = self._ai_extract_entities(content, content_type, existing_tags, existing_entities)
            
            # Validate and enrich entities
            enriched_entities = self._enrich_entities(entities, content_type, existing_tags)
            
            if self.debug:
                print(f"✅ Extracted {len(enriched_entities)} entities")
                for entity in enriched_entities[:3]:
                    print(f"   - {entity['entity_name']} ({entity['entity_type']})")
            
            return enriched_entities
            
        except Exception as e:
            print(f"❌ Entity extraction failed: {e}")
            return []
    
    def _ai_extract_entities(self, content: str, content_type: str, existing_tags: List[str], 
                            existing_entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Use AI to extract entities from content"""
        
        # Format existing entities for context
        entity_context = self._format_entity_context(existing_entities)
        
        prompt = f"""You are an expert at extracting game entities from D&D world building content.

CONTENT TYPE: {content_type}
CONTENT TO ANALYZE: {content}

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
- deity: Gods/divine beings (Solara, Lunaris, Malakar)
- threat: Specific dangers (The Dread Titan, Shadow Plague)

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
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # Lower temperature for consistent extraction
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result.get('entities', [])
            
        except Exception as e:
            if self.debug:
                print(f"❌ AI entity extraction failed: {e}")
            return []
    
    def _get_existing_entities(self, campaign_id: str) -> Dict[str, List[str]]:
        """Get existing entities from database for consistency"""
        
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
                    entities[entity_type].append(f"{name}: {description[:50]}...")
                else:
                    entities['npc'].append(f"{name}: {description[:50]}...")  # Default fallback
            
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
                context_parts.append(f"{entity_type.upper()}S: {', '.join(entity_list[:5])}")
        
        return "\n".join(context_parts) if context_parts else "No existing entities found - create initial entity vocabulary."
    
    def _enrich_entities(self, entities: List[Dict[str, Any]], content_type: str, 
                        content_tags: List[str]) -> List[Dict[str, Any]]:
        """Enrich extracted entities with additional metadata"""
        
        enriched = []
        
        for entity in entities:
            # Validate required fields
            if not all(field in entity for field in ['entity_name', 'entity_type', 'description']):
                if self.debug:
                    print(f"⚠️ Skipping malformed entity: {entity}")
                continue
            
            # Add content relationship tags
            entity_tags = entity.get('suggested_tags', [])
            
            # Ensure entity connects to content
            entity_tags.extend([tag for tag in content_tags if tag not in entity_tags])
            
            # Add entity type tag
            if entity['entity_type'] not in entity_tags:
                entity_tags.append(entity['entity_type'])
            
            # Add content type connection
            if content_type not in entity_tags:
                entity_tags.append(content_type)
            
            # Clean up tags (remove duplicates, lowercase)
            entity_tags = list(set([tag.lower().replace(' ', '_') for tag in entity_tags]))
            
            enriched_entity = {
                'entity_name': entity['entity_name'].strip(),
                'entity_type': entity['entity_type'].lower(),
                'description': entity['description'].strip(),
                'extraction_context': entity.get('extraction_context', ''),
                'tags': entity_tags,
                'status': 'extracted',  # Will be 'generated' when detailed, 'detailed' when fully fleshed out
                'source_content_type': content_type
            }
            
            enriched.append(enriched_entity)
        
        return enriched
    
    def extract_entities_from_expansion(self, expanded_content: str, content_type: str, 
                                      parent_tags: List[str], campaign_id: str) -> List[Dict[str, Any]]:
        """
        Extract entities from expanded content, connecting to parent content
        
        Args:
            expanded_content: The expanded narrative content
            content_type: Type of content being expanded
            parent_tags: Tags from the original content
            campaign_id: Campaign UUID
            
        Returns:
            List of extracted entities with parent relationships
        """
        if self.debug:
            print(f"🔄 Extracting entities from expanded {content_type}")
        
        # Extract entities normally
        entities = self.extract_entities(expanded_content, content_type, parent_tags, campaign_id)
        
        # Mark as expansion entities
        for entity in entities:
            entity['status'] = 'expansion_extracted'
            entity['tags'].append('detailed')
            entity['tags'].append('expanded')
        
        return entities
    
    def validate_entity_consistency(self, new_entities: List[Dict[str, Any]], 
                                  campaign_id: str) -> List[Dict[str, Any]]:
        """
        Validate that new entities don't conflict with existing ones
        
        Args:
            new_entities: List of newly extracted entities
            campaign_id: Campaign UUID
            
        Returns:
            List of validated entities (may have name adjustments)
        """
        if self.debug:
            print(f"🔍 Validating {len(new_entities)} entities for consistency")
        
        try:
            existing_entities = self._get_existing_entities(campaign_id)
            existing_names = []
            
            for entity_list in existing_entities.values():
                for entity_desc in entity_list:
                    name = entity_desc.split(':')[0].strip()
                    existing_names.append(name.lower())
            
            validated = []
            
            for entity in new_entities:
                entity_name = entity['entity_name'].lower()
                
                # Check for exact duplicates
                if entity_name in existing_names:
                    if self.debug:
                        print(f"⚠️ Found duplicate entity: {entity['entity_name']}")
                    # Keep the entity but mark it as duplicate
                    entity['status'] = 'duplicate_detected'
                    entity['tags'].append('needs_review')
                
                validated.append(entity)
            
            return validated
            
        except Exception as e:
            if self.debug:
                print(f"❌ Entity validation failed: {e}")
            return new_entities  # Return unvalidated if validation fails 