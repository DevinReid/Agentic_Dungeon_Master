#!/usr/bin/env python3
"""
Tag Generator Agent

AI-powered tag generation with consistency learning.
Analyzes existing tag patterns to maintain consistency across content.
"""

import json
from typing import List, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class TagGeneratorAgent:
    """AI bot that generates consistent tags for world content"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if self.debug:
            print("🏷️ TagGeneratorAgent initialized")
    
    def generate_tags(self, content: str, content_type: str, campaign_id: str, 
                     metadata: Dict = None, is_expansion: bool = False) -> List[str]:
        """
        Generate consistent tags for content using existing vocabulary patterns
        
        Args:
            content: The narrative text content
            content_type: Type of content ('pantheon', 'magic_system', etc.)
            campaign_id: Campaign UUID for consistency context
            metadata: Optional structured metadata
            is_expansion: Whether this is expanded content
            
        Returns:
            List of generated tags
        """
        if self.debug:
            print(f"🏷️ Generating tags for {content_type}")
        
        try:
            # Get existing tag vocabulary for consistency
            existing_vocab = self._get_existing_vocabulary(campaign_id)
            
            # Generate tags using AI
            tags = self._ai_generate_tags(content, content_type, existing_vocab, metadata, is_expansion)
            
            # Update tag vocabulary for future consistency
            self._update_tag_vocabulary(campaign_id, tags, content_type)
            
            if self.debug:
                print(f"✅ Generated {len(tags)} tags: {tags[:5]}{'...' if len(tags) > 5 else ''}")
            
            return tags
            
        except Exception as e:
            print(f"❌ Tag generation failed: {e}")
            # Return basic fallback tags
            return [content_type, 'generated_content']
    
    def _ai_generate_tags(self, content: str, content_type: str, existing_vocab: Dict, 
                         metadata: Dict = None, is_expansion: bool = False) -> List[str]:
        """Use AI to generate appropriate tags"""
        
        # Prepare context about existing tags
        vocab_context = self._format_vocabulary_context(existing_vocab)
        
        # Prepare metadata context if available
        metadata_context = ""
        if metadata:
            key_fields = self._extract_key_metadata_fields(metadata, content_type)
            if key_fields:
                metadata_context = f"\nSTRUCTURED DATA: {json.dumps(key_fields, indent=2)}"
        
        expansion_note = ""
        if is_expansion:
            expansion_note = "\nThis is EXPANDED content - include 'detailed' and 'expanded' tags."
        
        prompt = f"""You are a tag generation expert for D&D world building content.

CONTENT TYPE: {content_type}
CONTENT TO TAG: {content[:1000]}{'...' if len(content) > 1000 else ''}
{metadata_context}
{expansion_note}

EXISTING TAG PATTERNS IN THIS CAMPAIGN:
{vocab_context}

TAGGING RULES:
1. Use existing entity names when referring to the same characters/places/concepts
2. Use existing category patterns (pantheon, magic_system, etc.)
3. Create new tags only for genuinely new concepts
4. Format: lowercase_with_underscores
5. Include content category tag ({content_type})
6. Include specific entity names mentioned
7. Include thematic concepts (fire_magic, divine_power, ancient_evil)
8. Include relationship tags (connects_to_magic, religious_conflict)

GOOD TAG EXAMPLES:
- Entity tags: solara, malakar, temple_of_dawn
- Theme tags: divine_magic, ancient_evil, fire_magic
- Category tags: pantheon, magic_system, global_threats
- Relationship tags: religious_conflict, magical_corruption
- Detail tags: detailed, expanded, cross_referenced

Generate 8-15 relevant tags that follow existing patterns.

Return ONLY a JSON object:
{{"tags": ["list", "of", "generated", "tags"]}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result.get('tags', [content_type])
            
        except Exception as e:
            if self.debug:
                print(f"❌ AI tag generation failed: {e}")
            return [content_type, 'ai_generated']
    
    def _get_existing_vocabulary(self, campaign_id: str) -> Dict[str, List[str]]:
        """Get existing tag patterns from database for consistency"""
        
        try:
            # Import here to avoid circular imports
            from db.db import get_db_connection
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get tag usage statistics
            cur.execute("""
                SELECT tag_name, tag_category, usage_count
                FROM tag_vocabulary 
                WHERE campaign_id = %s
                ORDER BY usage_count DESC
                LIMIT 50
            """, (campaign_id,))
            
            vocab_data = cur.fetchall()
            cur.close()
            conn.close()
            
            # Organize by category
            vocab = {
                'entities': [],
                'themes': [],
                'categories': [],
                'locations': [],
                'popular': []
            }
            
            for tag_name, category, count in vocab_data:
                vocab['popular'].append((tag_name, count))
                
                if category:
                    if category in vocab:
                        vocab[category].append(tag_name)
                    else:
                        vocab['themes'].append(tag_name)  # Default fallback
                else:
                    # Categorize by pattern if no explicit category
                    if not '_' in tag_name and tag_name[0].isupper():
                        vocab['entities'].append(tag_name.lower())
                    elif '_' in tag_name:
                        vocab['themes'].append(tag_name)
                    else:
                        vocab['categories'].append(tag_name)
            
            return vocab
            
        except Exception as e:
            if self.debug:
                print(f"⚠️ Could not get existing vocabulary: {e}")
            return {'entities': [], 'themes': [], 'categories': [], 'locations': [], 'popular': []}
    
    def _format_vocabulary_context(self, vocab: Dict[str, List[str]]) -> str:
        """Format vocabulary for AI prompt"""
        
        context_parts = []
        
        if vocab['popular']:
            top_tags = [tag for tag, count in vocab['popular'][:10]]
            context_parts.append(f"Most used tags: {', '.join(top_tags)}")
        
        if vocab['entities']:
            context_parts.append(f"Entity names: {', '.join(vocab['entities'][:8])}")
        
        if vocab['categories']:
            context_parts.append(f"Content categories: {', '.join(vocab['categories'][:6])}")
        
        if vocab['themes']:
            context_parts.append(f"Theme patterns: {', '.join(vocab['themes'][:10])}")
        
        if vocab['locations']:
            context_parts.append(f"Location patterns: {', '.join(vocab['locations'][:6])}")
        
        return "\n".join(context_parts) if context_parts else "No existing tags found - create initial tag vocabulary."
    
    def _extract_key_metadata_fields(self, metadata: Dict, content_type: str) -> Dict:
        """Extract key fields from metadata for tag generation context"""
        
        key_fields = {}
        
        if content_type == 'pantheon':
            relevant_fields = ['major_deities', 'structure', 'religious_conflicts']
        elif content_type == 'magic_system':
            relevant_fields = ['commonality', 'sources', 'magic_level', 'limitations']
        elif content_type == 'global_threats':
            relevant_fields = ['primary_threat', 'world_impact', 'resistance_forces']
        elif content_type == 'world_overview':
            relevant_fields = ['world_name', 'theme_list', 'natural_laws']
        else:
            relevant_fields = ['name', 'description', 'type', 'structure']
        
        for field in relevant_fields:
            if field in metadata:
                key_fields[field] = metadata[field]
        
        return key_fields
    
    def _update_tag_vocabulary(self, campaign_id: str, tags: List[str], content_type: str):
        """Update tag vocabulary tracking for future consistency"""
        
        try:
            from db.db import get_db_connection
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            for tag in tags:
                # Determine tag category
                category = self._categorize_tag(tag, content_type)
                
                # Insert or update tag usage
                cur.execute("""
                    INSERT INTO tag_vocabulary (campaign_id, tag_name, tag_category, usage_count)
                    VALUES (%s, %s, %s, 1)
                    ON CONFLICT (campaign_id, tag_name)
                    DO UPDATE SET 
                        usage_count = tag_vocabulary.usage_count + 1,
                        last_used = CURRENT_TIMESTAMP
                """, (campaign_id, tag, category))
            
            conn.commit()
            cur.close()
            conn.close()
            
            if self.debug:
                print(f"📊 Updated vocabulary with {len(tags)} tags")
                
        except Exception as e:
            if self.debug:
                print(f"⚠️ Could not update tag vocabulary: {e}")
    
    def _categorize_tag(self, tag: str, content_type: str) -> str:
        """Automatically categorize a tag"""
        
        # Category tags
        if tag in ['pantheon', 'magic_system', 'global_threats', 'world_overview', 'regional_overview']:
            return 'category'
        
        # Detail level tags
        if tag in ['detailed', 'expanded', 'base', 'cross_referenced']:
            return 'detail_level'
        
        # Entity patterns (proper nouns, usually no underscores)
        if not '_' in tag and tag[0].isupper():
            return 'entity'
        
        # Theme patterns (descriptive, with underscores)
        if '_' in tag:
            if 'temple' in tag or 'castle' in tag or 'mountain' in tag:
                return 'location'
            elif 'magic' in tag or 'divine' in tag or 'evil' in tag:
                return 'theme'
            else:
                return 'relationship'
        
        # Default fallback
        return 'theme' 