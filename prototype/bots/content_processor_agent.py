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

# Import the processing bots
from .tag_generator_agent import TagGeneratorAgent
from .entity_extractor_agent import EntityExtractorAgent
# TODO: Insert chunker functionality here - build ContentChunkerAgent together
# from .content_chunker_agent import ContentChunkerAgent

load_dotenv()

class ContentProcessorAgent:
    """AI-powered content processor that enriches raw AI output"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize processing bots
        self.tag_generator = TagGeneratorAgent(debug=debug)
        self.entity_extractor = EntityExtractorAgent(debug=debug)
        # TODO: Insert chunker initialization here - build ContentChunkerAgent together
        # self.content_chunker = ContentChunkerAgent(debug=debug)
        
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
                entities = self.entity_extractor.extract_entities(
                    content=narrative_content,
                    content_type=content_type,
                    existing_tags=tags,
                    campaign_id=campaign_id
                )
                
                # Step 3: Create chunks for vector embedding
                # TODO: Insert chunker functionality here - build ContentChunkerAgent.create_chunks() together
                # chunks = self.content_chunker.create_chunks(
                #     content=narrative_content,
                #     content_type=content_type,
                #     tags=tags,
                #     entities=entities
                # )
                # Temporary placeholder chunks until we build the chunker
                chunks = self._create_placeholder_chunks(narrative_content, content_type, tags, entities)
                
                processed_section = {
                    'section_key': section_key,
                    'content_type': content_type,
                    'source_type': 'universe_builder',
                    'title': self._generate_title(section_key, section_data),
                    'narrative_content': narrative_content,
                    'original_metadata': section_data,
                    'tags': tags,
                    'entities': entities,
                    'chunks': chunks
                }
                
                processed_sections.append(processed_section)
                
                if self.debug:
                    print(f"✅ Processed {section_key}: {len(tags)} tags, {len(entities)} entities, {len(chunks)} chunks")
                    
            except Exception as e:
                print(f"❌ Error processing {section_key}: {e}")
                continue
        
        if self.debug:
            print(f"🎯 Processed {len(processed_sections)} sections total")
        
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
            
            entities = self.entity_extractor.extract_entities(
                content=expanded_content,
                content_type=content_type,
                existing_tags=tags,
                campaign_id=campaign_id
            )
            
            # TODO: Insert chunker functionality here - build ContentChunkerAgent.create_chunks() together
            # chunks = self.content_chunker.create_chunks(
            #     content=expanded_content,
            #     content_type=content_type,
            #     tags=tags,
            #     entities=entities
            # )
            # Temporary placeholder chunks until we build the chunker
            chunks = self._create_placeholder_chunks(expanded_content, content_type, tags, entities)
            
            return {
                'content_type': content_type,
                'source_type': 'expansion_bot',
                'title': f"Expanded {content_type.replace('_', ' ').title()}",
                'narrative_content': expanded_content,
                'tags': tags,
                'entities': entities,
                'chunks': chunks,
                'parent_content_id': parent_content_id
            }
            
        except Exception as e:
            print(f"❌ Error processing expansion content: {e}")
            raise
    
    def _create_placeholder_chunks(self, content: str, content_type: str, 
                                 tags: List[str], entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Temporary placeholder method until we build the ContentChunkerAgent together
        Creates simple chunks for now so the system doesn't crash
        """
        # Simple placeholder: create one chunk with all the content
        word_count = len(content.split())
        
        # Extract entity names for metadata
        entity_names = [entity.get('entity_name', '') for entity in entities]
        
        placeholder_chunk = {
            'index': 0,
            'text': content,
            'topic': f"{content_type.replace('_', ' ').title()} Overview",
            'word_count': word_count,
            'chunk_type': 'placeholder',
            'content_type': content_type,
            'tags': tags,
            'entities_mentioned': [{'name': name, 'type': 'unknown', 'tags': []} for name in entity_names],
            'embedding_metadata': {
                'content_type': content_type,
                'chunk_topic': f"{content_type} overview",
                'chunk_index': 0,
                'entity_names': entity_names
            }
        }
        
        return [placeholder_chunk] 