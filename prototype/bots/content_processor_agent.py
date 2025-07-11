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
from db.db import save_world_content, update_tag_vocabulary_batch, update_world_full_json

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
            print("🔄 Processing universe content in batch mode")
        
        #* 1. Save full universe JSON to worlds.full_json
        update_world_full_json(world_id, universe_data)

        # ? test refactor
        #* 2. Extract all narrative content from sections
        combined_narrative, section_data_list, combined_metadata = self._extract_world_narrative_content(universe_data)
        
        #*3. Generate tags for ALL content in ONE AI call -
        # ! doesnt this not work if they tags arent attached to the content?
        # ! not sure about this but ill leave it alone for now
        if self.debug:
            print("🏷️ Generating tags for all content in ONE AI call...")
        
        all_tags = self.tag_generator.generate_tags(
            content=combined_narrative,
            content_type='universe_content',  # Combined content type
            campaign_id=campaign_id,
            metadata=combined_metadata
        )
        
        # Capture raw tag generation response
        raw_tag_response = getattr(self.tag_generator, '_last_raw_response', None)
        
         
        #* 4. Extract entities from ALL content in ONE AI call and save directly
        # * needs tags, narrative extractor
        # * Note: Entities are saved directly to database here (step 7 functionality)
        if self.debug:
            print("🔍 Extracting entities from all content in ONE AI call...")
        all_entities_grouped = self.entity_extractor.extract_entities(
            content=combined_narrative,
            content_type='universe_content',
            existing_tags=all_tags,
            campaign_id=campaign_id,
            world_id=world_id,
            save_direct=True  # Save processed entities directly to database
        )
        
        # Capture raw entity extraction response
        raw_entity_response = getattr(self.entity_extractor, '_last_raw_response', None)
        
        #* 5. Create chunks for ALL content in ONE AI call
        # * needs narrative extractor and taggenator
        if self.debug:
            print("📄 Chunking all content in ONE AI call...")
        
        all_chunks = self.content_chunker.create_chunks(
            content=combined_narrative,
            content_type='universe_content',
            tags=all_tags
        )
        
        # Capture raw chunking response for debug printout
        raw_chunk_response = getattr(self.content_chunker, '_last_raw_response', None)
        
        #* 6. Save individual sections to world_content and link entities

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
                title=section_data['title']
            )
            
            section_content_ids[section_data['content_type']] = content_id
            section_data['content_id'] = content_id
            section_data['tags'] = all_tags  # All sections share the same tags
            processed_sections.append(section_data)
        
        #* 8. Vectorize chunks directly to Pinecone
        if all_chunks:
            if self.debug:
                print(f"🔍 Vectorizing {len(all_chunks)} chunks directly to Pinecone...")
            self._vectorize_chunks_direct(all_chunks, campaign_id, world_id, 'universe_content')
        
        #* 9. Upsert all tags into tag_vocabulary
        update_tag_vocabulary_batch(campaign_id, list(all_tags), 'world_content')
        
        if self.debug:
            print("✅ Batch processing complete:")
            print(f"   - 1 AI call for tags (generated {len(all_tags)} tags)")
            print("   - 1 AI call for entity extraction and processing")
            print(f"   - 1 AI call for content chunking (generated {len(all_chunks)} chunks)")
        
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
    
    def _extract_world_narrative_content(self, universe_data: dict) -> tuple[str, list, dict]:
        """Extract all narrative content from sections and return combined narrative, section list, and metadata"""
        
        # Define processable sections
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
            
            # Extract narrative content based on section type
            if isinstance(section_data, str):
                narrative_content = section_data
            elif isinstance(section_data, dict):
                # Collect ALL narrative fields, not just the first one
                narrative_fields = [
                    'description', 'world_description', 'theme_description', 'natural_laws', 'custom_details',
                    'mechanics', 'commonality', 'limitations', 'sources',
                    'structure', 'major_deities', 'religious_conflicts', 'divine_influence',
                    'threat_details', 'world_impact', 'resistance_forces'
                ]
                
                narrative_parts = []
                for field in narrative_fields:
                    if field in section_data and isinstance(section_data[field], str) and len(section_data[field].strip()) > 10:
                        narrative_parts.append(section_data[field])
                
                if narrative_parts:
                    narrative_content = " ".join(narrative_parts)
                else:
                    # Fallback: convert entire dict to descriptive text
                    narrative_content = self._dict_to_narrative(section_data)
            elif isinstance(section_data, list):
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
                    narrative_content = " ".join(threat_texts)
                else:
                    # Convert list items to narrative
                    narrative_content = " ".join([str(item) for item in section_data if isinstance(item, str)])
            else:
                narrative_content = str(section_data)
            
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
        
        return combined_narrative, section_data_list, combined_metadata
    
    def _dict_to_narrative(self, data: dict) -> str:
        # ! fall back for when narrative extractor fails, not sure if we need this
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

    # ? maybe move to vector service?
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
    # *
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
        
        print(f"✅ Debug output saved: {json_filename}")
    
 