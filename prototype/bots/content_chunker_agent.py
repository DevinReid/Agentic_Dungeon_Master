#!/usr/bin/env python3
"""
Content Chunker Agent

AI-powered content chunking that creates semantically coherent chunks for vector embedding.
Uses tags and entities to determine optimal chunk boundaries.
"""

import json
from typing import List, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class ContentChunkerAgent:
  
    def __init__(self, debug=False):
        self.debug = debug
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Chunk size parameters (in words)
        self.target_chunk_size = 400      # Target words per chunk
        self.max_chunk_size = 800         # Maximum chunk size
        self.overlap_size = 50            # Word overlap between chunks
        
        if self.debug:
            print("📋 ContentChunkerAgent initialized")
    
    def create_chunks(self, content: str, content_type: str, tags: List[str]) -> List[Dict[str, Any]]:
        """
        Create semantically coherent chunks for vector embedding
        
        Args:
            content: The narrative text content
            content_type: Type of content ('pantheon', 'magic_system', etc.)
            tags: Tags associated with this content
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if self.debug:
            print(f"📋 Creating chunks for {content_type}")
        
        try:
            # Single AI call for semantic chunking with pronoun resolution
            chunks = self._ai_semantic_chunk(content, content_type, tags)
            
            # Validate and enrich chunks with metadata
            enriched_chunks = self._enrich_chunks(chunks, content_type, tags)
            
            if self.debug:
                print(f"✅ Created {len(enriched_chunks)} chunks")
                for i, chunk in enumerate(enriched_chunks[:3]):
                    print(f"   - Chunk {i+1}: {len(chunk['text'].split())} words, topic: {chunk['topic']}")
            
            return enriched_chunks
            
        except Exception as e:
            print(f"❌ Content chunking failed: {e}")
            print(f"❌ DEBUG: Exception type: {type(e)}")
            print(f"❌ DEBUG: Exception args: {e.args}")
            import traceback
            print(f"❌ DEBUG: Full traceback:")
            traceback.print_exc()
            
            # Fallback to simple word-count chunking (no AI processing)
            return self._simple_chunk_fallback(content, content_type, tags)
    
    def _ai_semantic_chunk(self, content: str, content_type: str, tags: List[str]) -> List[Dict[str, Any]]:
        """AI call that analyzes semantic structure and creates chunks with pronoun resolution"""
        
        # AI call that analyzes semantic structure and creates chunks with pronoun resolution
        
        # Simple quote escaping to avoid JSON parsing issues
        escaped_content = content.replace('"', "'").replace('\n', ' ').replace('\r', '')
        
        prompt = f"""Analyze and chunk this {content_type} content for vector embedding in one step.

                            CONTENT: {escaped_content}

                            TAGS: {', '.join(tags)}

                            TASK: Analyze the semantic structure and create optimal chunks with pronoun resolution.

                            CHUNKING RULES:
                            1. Target {self.target_chunk_size} words per chunk (flexible based on semantic boundaries)
                            2. Each chunk should focus on one main concept/topic
                            3. Include {self.overlap_size} word overlap between consecutive chunks for context
                            4. Don't exceed {self.max_chunk_size} words per chunk
                            5. Find natural semantic boundaries (topic shifts, entity transitions)
                            6. Preserve narrative flow and context
                            7. CRITICAL: Replace pronouns (he, she, they, it, there, then, this, that) with appropriate proper nouns for better vector search

                            PRONOUN RESOLUTION:
                            - "He ruled wisely" → "Lord Dino ruled wisely"
                            - "It was magnificent" → "The Crystal Palace was magnificent" 
                            - "They gathered there" → "The Council gathered in the Sacred Grove"
                            - Only replace pronouns with clear referents from the content
                            - Maintain natural readability

                            For each chunk, provide:
                            - text: The chunk content with proper boundaries AND resolved pronouns
                            - topic: Main topic/focus of this chunk  
                            - word_count: Approximate word count
                            - chunk_type: 'entity_focused', 'narrative', 'descriptive', 'mechanical'

                            Return JSON:
                            {{
                            "chunks": [
                                {{
                                "text": "chunk content here with semantic boundaries and resolved pronouns...",
                                "topic": "Solara's divine domains and powers",
                                "word_count": 380,
                                "chunk_type": "entity_focused"
                                }}
                            ]
                            }}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o which supports structured output
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # Lower temperature for consistent chunking
                max_tokens=2000,
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
            chunks = result.get('chunks', [])
            
            return chunks
            
        except Exception as e:
            if self.debug:
                print(f"❌ AI semantic chunking failed: {e}")
                print(f"❌ DEBUG: Exception type: {type(e)}")
                import traceback
                traceback.print_exc()
            return []
    
    def _enrich_chunks(self, chunks: List[Dict[str, Any]], content_type: str, 
                      content_tags: List[str]) -> List[Dict[str, Any]]:
        """Enrich chunks with additional metadata"""
        
        enriched = []
        
        for i, chunk in enumerate(chunks):
            # Validate chunk structure
            if not isinstance(chunk, dict) or 'text' not in chunk:
                continue
            
            # Calculate actual word count
            actual_word_count = len(chunk['text'].split())
            
            # Skip chunks that are too large
            if actual_word_count > self.max_chunk_size:
                continue
            
            # Create chunk tags (use content tags)
            chunk_tags = content_tags.copy()
            
            # Remove duplicates and clean up
            chunk_tags = list(set([tag.lower().replace(' ', '_') for tag in chunk_tags]))
            
            enriched_chunk = {
                'index': i,
                'text': chunk['text'].strip(),
                'topic': chunk.get('topic', f"{content_type} content"),
                'word_count': actual_word_count,
                'chunk_type': chunk.get('chunk_type', 'narrative'),
                'content_type': content_type,
                'tags': chunk_tags,
                'entities_mentioned': [],  # No entity enrichment needed
                'embedding_metadata': {
                    'content_type': content_type,
                    'chunk_topic': chunk.get('topic', ''),
                    'chunk_index': i,
                    'entity_names': []  # No entity names needed
                }
            }
            
            enriched.append(enriched_chunk)
        
        return enriched
    
    def _simple_chunk_fallback(self, content: str, content_type: str, tags: List[str]) -> List[Dict[str, Any]]:
        """Simple fallback chunking when AI chunking fails"""
        
        words = content.split()
        chunks = []
        
        # Simple word-count based chunking
        chunk_size = self.target_chunk_size
        overlap = self.overlap_size
        
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_words) > 0:  # Accept any non-empty chunk
                chunks.append({
                    'index': chunk_index,
                    'text': chunk_text,
                    'topic': f"{content_type} content",
                    'word_count': len(chunk_words),
                    'chunk_type': 'narrative',
                    'content_type': content_type,
                    'tags': tags,
                    'entities_mentioned': [],
                    'embedding_metadata': {
                        'content_type': content_type,
                        'chunk_topic': f"{content_type} content",
                        'chunk_index': chunk_index,
                        'entity_names': []
                    }
                })
                chunk_index += 1
            
            # Move start position with overlap
            start = start + chunk_size - overlap
            
            if start >= len(words):
                break
        
        return chunks
        
        return chunks 