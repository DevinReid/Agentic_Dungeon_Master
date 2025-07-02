#!/usr/bin/env python3
"""
Vector service for managing OpenAI embeddings and Pinecone vector storage.

This service handles:
1. Generating embeddings from text using OpenAI
2. Storing/retrieving vectors in Pinecone  
3. Semantic search across world content
4. Metadata linking back to PostgreSQL records
"""

import os
import hashlib
import json
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class VectorService:
    """Service for managing embeddings and vector operations"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize Pinecone
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
            
        # Initialize pinecone client
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "dnd-world-content")
        
        # Connect to index (will be created if it doesn't exist)
        self.index = self._get_or_create_index()
        
        if self.debug:
            print("✅ VectorService initialized")
        
        try:
            stats = self.index.describe_index_stats()
            total_vectors = stats['total_vector_count']
            print(f"✅ Connected to Pinecone index '{self.index_name}' with {total_vectors} vectors")
        except Exception as e:
            print(f"⚠️ Could not get Pinecone stats: {e}")
    
    def _get_or_create_index(self):
        """Get existing index or create a new one"""
        try:
            # Try to connect to existing index
            index = self.pc.Index(self.index_name)
            
            # Test connection
            stats = index.describe_index_stats()
            print(f"✅ Connected to Pinecone index '{self.index_name}' with {stats['total_vector_count']} vectors")
            return index
            
        except Exception as e:
            print(f"⚠️ Index '{self.index_name}' not found or connection failed: {e}")
            print("🔧 Creating new Pinecone index...")
            
            # Create new index with OpenAI embedding dimensions
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI text-embedding-ada-002 dimensions
                metric='cosine',  # Good for text similarity
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
            )
            
            print(f"✅ Created new Pinecone index: {self.index_name}")
            return self.pc.Index(self.index_name)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text.strip()
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Failed to generate embedding: {e}")
            raise
    
    def create_vector_id(self, content_id: str, content_type: str) -> str:
        """Create a unique vector ID for Pinecone"""
        # Combine content_id and content_type to create unique vector ID
        unique_string = f"{content_id}:{content_type}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def store_world_content_embedding(self, 
                                    content_id: str,
                                    campaign_id: str, 
                                    world_id: str,
                                    content_type: str,
                                    title: str,
                                    text: str) -> str:
        """Store world content embedding in Pinecone
        
        Args:
            content_id: UUID from world_content table
            campaign_id: Campaign UUID
            world_id: World UUID  
            content_type: Type of content (world_info, magic_system, etc.)
            title: Content title
            text: The actual text content to embed
            
        Returns:
            vector_id: The Pinecone vector ID
        """
        try:
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Create unique vector ID
            vector_id = self.create_vector_id(content_id, content_type)
            
            # Metadata for linking back to PostgreSQL
            metadata = {
                "content_id": content_id,
                "campaign_id": campaign_id,
                "world_id": world_id,
                "content_type": content_type,
                "title": title,
                "text_snippet": text[:500] + "..." if len(text) > 500 else text  # Store preview
            }
            
            # Store in Pinecone
            self.index.upsert(vectors=[(vector_id, embedding, metadata)])
            
            print(f"✅ Stored embedding for {content_type}: {title}")
            return vector_id
            
        except Exception as e:
            print(f"❌ Failed to store embedding: {e}")
            raise
    
    def semantic_search(self, 
                       query: str, 
                       campaign_id: str = None,
                       content_types: List[str] = None,
                       top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search across world content
        
        Args:
            query: The search query text
            campaign_id: Optional campaign filter
            content_types: Optional content type filters
            top_k: Number of results to return
            
        Returns:
            List of matching content with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Build filter for metadata
            filter_dict = {}
            if campaign_id:
                filter_dict["campaign_id"] = campaign_id
            if content_types:
                filter_dict["content_type"] = {"$in": content_types}
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "content_id": match.metadata["content_id"],
                    "score": match.score,
                    "content_type": match.metadata["content_type"],
                    "title": match.metadata["title"],
                    "text_snippet": match.metadata["text_snippet"],
                    "campaign_id": match.metadata["campaign_id"],
                    "world_id": match.metadata["world_id"]
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Semantic search failed: {e}")
            return []
    
    def get_related_content(self, 
                          content_id: str, 
                          campaign_id: str = None,
                          top_k: int = 3) -> List[Dict[str, Any]]:
        """Find content related to a specific piece of content
        
        Args:
            content_id: The source content ID
            campaign_id: Optional campaign filter
            top_k: Number of related items to return
            
        Returns:
            List of related content
        """
        try:
            # Get the source vector
            vector_id = self.create_vector_id(content_id, "search")  # We'll need content_type for this
            
            # For now, we'll search by retrieving the content and doing similarity
            # This is a simplified version - in practice you'd want to cache embeddings
            
            # Build filter
            filter_dict = {"content_id": {"$ne": content_id}}  # Exclude the source content
            if campaign_id:
                filter_dict["campaign_id"] = campaign_id
            
            # This would need the actual implementation based on your specific needs
            # For now, returning empty list
            return []
            
        except Exception as e:
            print(f"❌ Related content search failed: {e}")
            return []
    
    def delete_world_content_embeddings(self, world_id: str):
        """Delete all embeddings for a specific world"""
        try:
            # Pinecone doesn't have a direct "delete by metadata" function
            # We'd need to query first, then delete by IDs
            # This is a placeholder for the proper implementation
            print(f"🗑️ Would delete embeddings for world_id: {world_id}")
            
        except Exception as e:
            print(f"❌ Failed to delete embeddings: {e}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.get('total_vector_count', 0),
                "dimension": stats.get('dimension', 0),
                "index_fullness": stats.get('index_fullness', 0.0)
            }
        except Exception as e:
            print(f"❌ Failed to get index stats: {e}")
            return {}
    
    def store_content_chunk_embedding(self, 
                                     content_id: str,
                                     campaign_id: str, 
                                     world_id: str,
                                     chunk_data: Dict[str, Any]) -> str:
        """Store content chunk embedding in Pinecone
        
        Args:
            content_id: UUID from world_content table
            campaign_id: Campaign UUID
            world_id: World UUID  
            chunk_data: Chunk data from ContentChunker with metadata
            
        Returns:
            vector_id: The Pinecone vector ID
        """
        try:
            # Generate embedding from chunk text
            embedding = self.generate_embedding(chunk_data['text'])
            
            # Create unique vector ID for this chunk
            vector_id = f"{content_id}_chunk_{chunk_data['index']}"
            
            # Metadata for linking back to PostgreSQL and filtering
            metadata = {
                "content_id": content_id,
                "campaign_id": campaign_id,
                "world_id": world_id,
                "content_type": chunk_data['content_type'],
                "chunk_topic": chunk_data['topic'],
                "chunk_type": chunk_data['chunk_type'],
                "tags": chunk_data['tags'][:10],  # Limit tags for metadata size
                "entity_names": [e['name'] for e in chunk_data['entities_mentioned']],
                "text_snippet": chunk_data['text'][:500] + "..." if len(chunk_data['text']) > 500 else chunk_data['text'],
                "word_count": chunk_data['word_count'],
                "is_expansion": chunk_data['embedding_metadata'].get('is_expansion', False)
            }
            
            # Store in Pinecone
            self.index.upsert(vectors=[(vector_id, embedding, metadata)])
            
            if self.debug:
                print(f"✅ Stored chunk embedding: {chunk_data['topic']} ({chunk_data['word_count']} words)")
            
            return vector_id
            
        except Exception as e:
            if self.debug:
                print(f"❌ Failed to store chunk embedding: {e}")
            raise 