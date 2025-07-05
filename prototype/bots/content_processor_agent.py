#!/usr/bin/env python3
"""
Content Processor Agent

Central orchestrator for processing raw AI content into enriched, database-ready data.
Coordinates tag generation, entity extraction, and content chunking.
"""

import json
from typing import Dict, List, Any
from openai import OpenAI
import os
from dotenv import load_dotenv
import psycopg2.extras
from db.db import save_world_content, get_db_connection, _update_tag_vocabulary_batch

# Import the processing bots
from .tag_generator_agent import TagGeneratorAgent
from .entity_extractor_agent import EntityExtractorAgent
from .content_chunker_agent import ContentChunkerAgent

load_dotenv()

class ContentProcessorAgent:
    """AI-powered content processor that enriches raw AI output"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize processing bots
        self.tag_generator = TagGeneratorAgent(debug=debug)
        self.entity_extractor = EntityExtractorAgent(debug=debug)
        self.content_chunker = ContentChunkerAgent(debug=debug)
        
        if self.debug:
            print("🤖 ContentProcessorAgent initialized with processing bots")
    
    def process_universe_content(self, campaign_id: str, universe_data: dict) -> List[Dict[str, Any]]:
        """
        Process raw UniverseBuilder output into enriched, database-ready content
        
        Args:
            campaign_id: Campaign UUID for context and tag consistency
            universe_data: Raw JSON from UniverseBuilder
            
        Returns:
            List of processed content sections ready for database storage
        """
        if self.debug:
            print(f"🏗️ Processing universe content for campaign {campaign_id}")
        
        processed_sections = []
        
        # Define which sections to process
        processable_sections = {
            'world_info': 'world_overview',
            'magic_system': 'magic_system', 
            'pantheon': 'pantheon',
            'global_threats': 'global_threats',
            'size': 'world_scale'
        }
        
        for section_key, content_type in processable_sections.items():
            if section_key not in universe_data:
                continue
                
            section_data = universe_data[section_key]
            
            if self.debug:
                print(f"📝 Processing section: {section_key} -> {content_type}")
            
            # Extract narrative content from the section
            narrative_content = self._extract_narrative_content(section_data, section_key)
            
            if not narrative_content:
                if self.debug:
                    print(f"⚠️ No narrative content found in {section_key}, skipping")
                continue
            
            try:
                # Step 1: Generate tags (foundation for everything else)
                tags = self.tag_generator.generate_tags(
                    content=narrative_content,
                    content_type=content_type,
                    campaign_id=campaign_id,
                    metadata=section_data
                )
                
                # Step 2: Extract entities (uses tags for consistency)
                entities_grouped = self.entity_extractor.extract_entities(
                    content=narrative_content,
                    content_type=content_type,
                    existing_tags=tags,
                    campaign_id=campaign_id
                )
                
                # Flatten entities for content chunker (expects flat list with 'name' field)
                entities_flat = self._flatten_entities_for_chunker(entities_grouped)
                
                # Step 3: Create chunks for vector embedding
                chunks = self.content_chunker.create_chunks(
                    content=narrative_content,
                    content_type=content_type,
                    tags=tags,
                    entities=entities_flat
                )
                
                processed_section = {
                    'section_key': section_key,
                    'content_type': content_type,
                    'source_type': 'universe_builder',
                    'title': self._generate_title(section_key, section_data),
                    'narrative_content': narrative_content,
                    'original_metadata': section_data,
                    'tags': tags,
                    'entities': entities_grouped,  # Keep grouped format for database saving
                    'entities_flat': entities_flat,  # Flat format for compatibility
                    'chunks': chunks
                }
                
                processed_sections.append(processed_section)
                
                if self.debug:
                    total_entities = sum(len(entities) for entities in entities_grouped.values())
                    print(f"✅ Processed {section_key}: {len(tags)} tags, {total_entities} entities, {len(chunks)} chunks")
                    
            except Exception as e:
                print(f"❌ Error processing {section_key}: {e}")
                continue
        
        if self.debug:
            print(f"🎯 Processed {len(processed_sections)} sections total")
        
        return processed_sections
    
    def process_universe_content_batch(self, campaign_id: str, universe_data: dict, world_id: str) -> List[Dict[str, Any]]:
        """
        Process universe content in efficient batches with single AI calls
        
        Args:
            campaign_id: Campaign UUID
            universe_data: Full universe data from UniverseBuilder
            world_id: World UUID for database saves
            
        Returns:
            List of processed content sections
        """
        if self.debug:
            print(f"🔄 Processing universe content in batch mode")
        
        # 1. Save full universe JSON to worlds.full_json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE worlds SET full_json = %s, updated_at = CURRENT_TIMESTAMP WHERE world_id = %s;
        """, (psycopg2.extras.Json(universe_data), world_id))
        conn.commit()
        cur.close()
        conn.close()
        
        # 2. Extract all narrative content from sections
        processable_sections = {
            'world_info': 'world_overview',
            'magic_system': 'magic_system', 
            'pantheon': 'pantheon',
            'global_threats': 'global_threats',
            'size': 'world_scale'
        }
        
        # Collect all narrative content and metadata
        all_narrative_content = []
        section_data_list = []
        
        for section_key, content_type in processable_sections.items():
            if section_key not in universe_data:
                continue
            section_data = universe_data[section_key]
            narrative_content = self._extract_narrative_content(section_data, section_key)
            title = self._generate_title(section_key, section_data)
            
            all_narrative_content.append(narrative_content)
            section_data_list.append({
                'section_key': section_key,
                'content_type': content_type,
                'source_type': 'universe_builder',
                'title': title,
                'narrative_content': narrative_content,
                'original_metadata': section_data
            })
        
        # Combine all narrative content for single AI calls
        combined_narrative = " ".join(all_narrative_content)
        combined_metadata = {section['section_key']: section['original_metadata'] for section in section_data_list}
        
        # 3. Generate tags for ALL content in ONE AI call
        if self.debug:
            print(f"🏷️ Generating tags for all content in ONE AI call...")
        
        all_tags = self.tag_generator.generate_tags(
            content=combined_narrative,
            content_type='universe_content',  # Combined content type
            campaign_id=campaign_id,
            metadata=combined_metadata
        )
        
        # Capture raw tag generation response
        raw_tag_response = getattr(self.tag_generator, '_last_raw_response', None)
        
        if self.debug:
            print(f"🔍 Extracting entities from all content in ONE AI call...")
        
        # 4. Extract entities from ALL content in ONE AI call
        all_entities_grouped = self.entity_extractor.extract_entities(
            content=combined_narrative,
            content_type='universe_content',
            existing_tags=all_tags,
            campaign_id=campaign_id,
            world_id=world_id,
            save_direct=False  # Don't save yet, we need to link to individual sections
        )
        
        # Capture raw entity extraction response
        raw_entity_response = getattr(self.entity_extractor, '_last_raw_response', None)
        
        if self.debug:
            print(f"📄 Chunking all content in ONE AI call...")
        
        # 5. Create chunks for ALL content in ONE AI call
        all_chunks = self.content_chunker.create_chunks(
            content=combined_narrative,
            content_type='universe_content',
            tags=all_tags
        )
        
        # Capture raw chunking response
        raw_chunk_response = getattr(self.content_chunker, '_last_raw_response', None)
        
        # 6. Save individual sections to world_content and link entities
        processed_sections = []
        section_content_ids = {}
        
        for section_data in section_data_list:
            # Save section to world_content
            content_id = save_world_content(
                world_id=world_id,
                campaign_id=campaign_id,
                content_type=section_data['content_type'],
                content_text=section_data['narrative_content'],
                metadata=section_data['original_metadata'],
                title=section_data['title'],
                create_embedding=False  # Do not save chunk embeddings to Postgres
            )
            
            section_content_ids[section_data['content_type']] = content_id
            section_data['content_id'] = content_id
            section_data['tags'] = all_tags  # All sections share the same tags
            processed_sections.append(section_data)
        
        # 7. Save entities with proper source_content_id linking
        # We need to distribute entities across sections based on content relevance
        if self.debug:
            print(f"💾 Saving entities with source content linking...")
        
        # For now, link all entities to the first section (world_info)
        # TODO: Could implement smarter entity-to-section matching
        primary_section = processed_sections[0] if processed_sections else None
        if primary_section and all_entities_grouped:
            # Process entities with batching (EntityProcessor handles the batching)
            from .entity_processor_agent import EntityProcessorAgent
            processor = EntityProcessorAgent(debug=self.debug)
            
            # Flatten entities for processing
            raw_entities = []
            for entity_type, entities in all_entities_grouped.items():
                for entity in entities:
                    if isinstance(entity, dict):
                        entity['entity_type'] = entity_type[:-1] if entity_type.endswith('s') else entity_type
                        raw_entities.append(entity)
            
            if raw_entities:
                processor.process_entities(
                    raw_entities=raw_entities,
                    campaign_id=campaign_id,
                    content=combined_narrative,
                    content_type='universe_content',
                    world_id=world_id,
                    save_direct=True,
                    source_content_id=primary_section['content_id']
                )
        
        # 8. Vectorize chunks directly to Pinecone
        if all_chunks:
            if self.debug:
                print(f"🔍 Vectorizing {len(all_chunks)} chunks directly to Pinecone...")
            self._vectorize_chunks_direct(all_chunks, campaign_id, world_id, 'universe_content')
        
        # 9. Upsert all tags into tag_vocabulary
        conn = get_db_connection()
        cur = conn.cursor()
        _update_tag_vocabulary_batch(campaign_id, list(all_tags), 'world_content', cur)
        conn.commit()
        cur.close()
        conn.close()
        
        if self.debug:
            print(f"✅ Batch processing complete:")
            print(f"   - 1 AI call for tags (generated {len(all_tags)} tags)")
            print(f"   - 1 AI call for entity extraction")
            print(f"   - 1 AI call for content chunking (generated {len(all_chunks)} chunks)")
            print(f"   - Entity processing in batches of 8")
        
        # 10. Save debug output to file for inspection
        if self.debug:
            self._save_debug_output(
                world_id=world_id,
                campaign_id=campaign_id,
                universe_data=universe_data,
                processed_sections=processed_sections,
                all_tags=all_tags,
                all_entities_grouped=all_entities_grouped,
                all_chunks=all_chunks,
                combined_narrative=combined_narrative,
                raw_tag_response=raw_tag_response,
                raw_entity_response=raw_entity_response,
                raw_chunk_response=raw_chunk_response
            )
        
        return processed_sections
    
    def _extract_narrative_content(self, section_data: Any, section_key: str) -> str:
        """Extract narrative text from structured section data"""
        
        if isinstance(section_data, str):
            return section_data
        
        if isinstance(section_data, dict):
            # Try common narrative field names
            narrative_fields = [
                'description', 'world_description', 'mechanics', 'structure', 
                'threat_details', 'commonality', 'summary'
            ]
            
            for field in narrative_fields:
                if field in section_data and isinstance(section_data[field], str):
                    return section_data[field]
            
            # Fallback: convert entire dict to descriptive text
            return self._dict_to_narrative(section_data)
        
        if isinstance(section_data, list):
            # For global_threats, it's a list - combine threat details
            if section_key == 'global_threats':
                threat_texts = []
                for threat in section_data:
                    if isinstance(threat, dict):
                        # Extract threat details and world impact
                        if 'threat_details' in threat:
                            threat_texts.append(threat['threat_details'])
                        if 'world_impact' in threat:
                            threat_texts.append(threat['world_impact'])
                        if 'primary_threat' in threat:
                            threat_texts.append(f"Known as: {threat['primary_threat']}")
                return " ".join(threat_texts)
            else:
                # Convert list items to narrative
                return " ".join([str(item) for item in section_data if isinstance(item, str)])
        
        return str(section_data)
    
    def _dict_to_narrative(self, data: dict) -> str:
        """Convert structured data to narrative text"""
        narrative_parts = []
        
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 20:  # Substantial text
                narrative_parts.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and len(item) > 10:
                        narrative_parts.append(item)
        
        return " ".join(narrative_parts)
    
    def _generate_title(self, section_key: str, section_data: Any) -> str:
        """Generate appropriate title for content section"""
        
        title_map = {
            'world_info': 'World Overview',
            'magic_system': 'Magic System',
            'pantheon': 'Divine Pantheon', 
            'global_threats': 'Global Threats',
            'size': 'World Scale'
        }
        
        base_title = title_map.get(section_key, section_key.replace('_', ' ').title())
        
        # Try to get more specific title from data
        if isinstance(section_data, dict):
            if 'world_name' in section_data:
                return f"{base_title} - {section_data['world_name']}"
            elif 'name' in section_data:
                return f"{base_title} - {section_data['name']}"
        
        return base_title
    
    def process_expansion_content(self, campaign_id: str, content_type: str, 
                                expanded_content: str, parent_content_id: str = None) -> Dict[str, Any]:
        """
        Process expanded content from expansion bots
        
        Args:
            campaign_id: Campaign UUID
            content_type: Type of content being expanded
            expanded_content: The expanded narrative content
            parent_content_id: ID of original content this expands
            
        Returns:
            Processed content ready for database storage
        """
        if self.debug:
            print(f"🔄 Processing expansion content for {content_type}")
        
        try:
            # Process the expanded content
            tags = self.tag_generator.generate_tags(
                content=expanded_content,
                content_type=content_type,
                campaign_id=campaign_id,
                is_expansion=True
            )
            
            entities_grouped = self.entity_extractor.extract_entities(
                content=expanded_content,
                content_type=content_type,
                existing_tags=tags,
                campaign_id=campaign_id
            )
            
            # Flatten entities for content chunker
            entities_flat = self._flatten_entities_for_chunker(entities_grouped)
            
            chunks = self.content_chunker.create_chunks(
                content=expanded_content,
                content_type=content_type,
                tags=tags,
                entities=entities_flat
            )
            
            return {
                'content_type': content_type,
                'source_type': 'expansion_bot',
                'title': f"Expanded {content_type.replace('_', ' ').title()}",
                'narrative_content': expanded_content,
                'tags': tags,
                'entities': entities_grouped,  # Keep grouped format for database saving
                'entities_flat': entities_flat,  # Flat format for compatibility
                'chunks': chunks,
                'parent_content_id': parent_content_id
            }
            
        except Exception as e:
            print(f"❌ Error processing expansion content: {e}")
            raise
    
    def _flatten_entities(self, entities_grouped: dict) -> list:
        """Flatten grouped entities into a flat list"""
        entities_flat = []
        for group, entities in entities_grouped.items():
            entities_flat.extend(entities)
        return entities_flat
    
    def _flatten_entities_for_chunker(self, entities_grouped: dict) -> list:
        """Flatten grouped entities into format expected by ContentChunker"""
        
        if self.debug:
            print(f"🔄 DEBUG: Flattening entities for chunker")
            print(f"🔄 DEBUG: Received grouped entities: {entities_grouped}")
            print(f"🔄 DEBUG: Groups: {list(entities_grouped.keys())}")
        
        entities_flat = []
        for group, entities in entities_grouped.items():
            if self.debug:
                print(f"🔄 DEBUG: Processing group '{group}' with {len(entities)} entities")
            
            for i, entity in enumerate(entities):
                if self.debug:
                    print(f"🔄 DEBUG: Processing entity {i+1} in group '{group}': {entity}")
                
                # Ensure we have a valid entity with all required fields
                if not isinstance(entity, dict):
                    if self.debug:
                        print(f"🔄 DEBUG: Skipping non-dict entity: {entity}")
                    continue
                
                # ContentChunker expects 'name' field, not 'entity_name'
                name = entity.get('name') or entity.get('entity_name', 'Unknown')
                
                # Determine entity_type with better fallback logic
                entity_type = entity.get('entity_type')
                if not entity_type:
                    # Try to infer from the group name
                    if group.endswith('s'):
                        entity_type = group[:-1]  # Remove 's' from plural
                    else:
                        entity_type = group
                
                # Ensure we have a valid entity_type
                if not entity_type or entity_type == 'Unknown':
                    entity_type = 'entity'  # Final fallback
                
                chunker_entity = {
                    'name': name,
                    'entity_type': entity_type,
                    'description': entity.get('description', ''),
                    'tags': entity.get('tags', [])
                }
                
                if self.debug:
                    print(f"🔄 DEBUG: Created chunker entity: {chunker_entity}")
                    print(f"     Original entity had 'entity_type': {'entity_type' in entity}")
                    print(f"     Original entity had 'name': {'name' in entity}")
                    print(f"     Original entity had 'entity_name': {'entity_name' in entity}")
                    print(f"     Final entity_type: {repr(entity_type)}")
                    print(f"     Final name: {repr(name)}")
                
                entities_flat.append(chunker_entity)
        
        if self.debug:
            print(f"🔄 DEBUG: Flattening complete: {len(entities_flat)} entities flattened")
            for i, entity in enumerate(entities_flat):
                print(f"   Flattened entity {i+1}: {entity}")
        
        return entities_flat
    
    def _vectorize_chunks_direct(self, chunks: List[Dict[str, Any]], campaign_id: str, world_id: str, section_key: str):
        """Send content chunks directly to vectorizer, bypassing ContentProcessor"""
        try:
            from services.vector_service import VectorService
            
            vector_service = VectorService(debug=self.debug)
            
            for chunk in chunks:
                # Create a content_id for the chunk since we're bypassing normal content save
                content_id = f"direct_{section_key}_{chunk['index']}"
                
                vector_service.store_content_chunk_embedding(
                    content_id=content_id,
                    campaign_id=campaign_id,
                    world_id=world_id,
                    chunk_data=chunk
                )
                
        except Exception as e:
            print(f"❌ Failed to vectorize chunks directly: {e}")
    
    def _save_debug_output(self, world_id: str, campaign_id: str, universe_data: dict, processed_sections: List[Dict[str, Any]], all_tags: List[str], all_entities_grouped: dict, all_chunks: List[Dict[str, Any]], combined_narrative: str, raw_tag_response: dict, raw_entity_response: dict, raw_chunk_response: dict):
        """Save debug output to file for inspection"""
        import datetime
        import os
        
        # Create a directory for debug outputs
        debug_dir = f"debug_outputs/{world_id}"
        os.makedirs(debug_dir, exist_ok=True)
        
        # Create a filename based on the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        json_filename = f"{debug_dir}/{world_id}_{campaign_id}_{timestamp}_debug_output.json"
        txt_filename = f"{debug_dir}/{world_id}_{campaign_id}_{timestamp}_debug_output.txt"
        
        # Prepare the debug output data
        debug_output = {
            'world_id': world_id,
            'campaign_id': campaign_id,
            'universe_data': universe_data,
            'processed_sections': processed_sections,
            'all_tags': all_tags,
            'all_entities_grouped': all_entities_grouped,
            'all_chunks': all_chunks,
            'combined_narrative': combined_narrative,
            'raw_tag_response': raw_tag_response,
            'raw_entity_response': raw_entity_response,
            'raw_chunk_response': raw_chunk_response
        }
        
        # Save the debug output to JSON file
        with open(json_filename, 'w') as f:
            json.dump(debug_output, f, indent=2)
        
        # Save human-readable text output
        with open(txt_filename, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("AGENTIC DUNGEON MASTER - DEBUG OUTPUT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"World ID: {world_id}\n")
            f.write(f"Campaign ID: {campaign_id}\n")
            f.write(f"Generated: {timestamp}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("ORIGINAL UNIVERSE DATA\n")
            f.write("=" * 80 + "\n")
            f.write(json.dumps(universe_data, indent=2))
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("COMBINED NARRATIVE CONTENT\n")
            f.write("=" * 80 + "\n")
            f.write(combined_narrative)
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("GENERATED TAGS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total tags: {len(all_tags)}\n")
            f.write("Tags: " + ", ".join(all_tags))
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("RAW TAG GENERATION RESPONSE\n")
            f.write("=" * 80 + "\n")
            if raw_tag_response:
                f.write("Raw AI response from TagGeneratorAgent:\n")
                f.write(json.dumps(raw_tag_response, indent=2))
            else:
                f.write("No raw response captured (agent may not support raw output)\n")
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("EXTRACTED ENTITIES\n")
            f.write("=" * 80 + "\n")
            for entity_type, entities in all_entities_grouped.items():
                f.write(f"\n{entity_type.upper()}:\n")
                for entity in entities:
                    f.write(f"  - {entity.get('entity_name', entity.get('name', 'Unknown'))}: {entity.get('description', 'No description')}\n")
            f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("RAW ENTITY EXTRACTION RESPONSE\n")
            f.write("=" * 80 + "\n")
            if raw_entity_response:
                f.write("Raw AI response from EntityExtractorAgent:\n")
                f.write(json.dumps(raw_entity_response, indent=2))
            else:
                f.write("No raw response captured (agent may not support raw output)\n")
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("CONTENT CHUNKS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total chunks: {len(all_chunks)}\n\n")
            for i, chunk in enumerate(all_chunks, 1):
                f.write(f"Chunk {i}:\n")
                f.write(f"  Topic: {chunk.get('topic', 'No topic')}\n")
                f.write(f"  Word count: {chunk.get('word_count', 'Unknown')}\n")
                f.write(f"  Content: {chunk.get('content', 'No content')}\n")
                f.write(f"  Tags: {', '.join(chunk.get('tags', []))}\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("RAW CONTENT CHUNKING RESPONSE\n")
            f.write("=" * 80 + "\n")
            if raw_chunk_response:
                f.write("Raw AI response from ContentChunkerAgent:\n")
                f.write(json.dumps(raw_chunk_response, indent=2))
            else:
                f.write("No raw response captured (agent may not support raw output)\n")
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("PROCESSED SECTIONS\n")
            f.write("=" * 80 + "\n")
            for section in processed_sections:
                f.write(f"\n{section['content_type'].upper()}:\n")
                f.write(f"  Title: {section['title']}\n")
                f.write(f"  Content: {section['narrative_content']}\n")
                f.write(f"  Content ID: {section.get('content_id', 'Not saved')}\n")
                f.write("\n")
        
        print(f"✅ Debug output saved:")
        print(f"   📄 JSON: {json_filename}")
        print(f"   📝 Text: {txt_filename}")
    
 