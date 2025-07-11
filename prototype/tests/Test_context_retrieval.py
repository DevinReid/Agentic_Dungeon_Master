#!/usr/bin/env python3
"""
Test script for context retrieval from Pinecone vector database
"""

import sys
import os
# Add the parent directory to the Python path so we can import from prototype
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vector_service import VectorService
from db.db import  get_db_connection


def explore_vector_database(campaign_id: str):
    """Explore what's actually in the vector database for this campaign"""
    
    print(f"🔍 EXPLORING VECTOR DATABASE FOR CAMPAIGN: {campaign_id}")
    print("="*60)
    
    # Initialize vector service
    vector_service = VectorService(debug=True)
    
    # Test 1: Get index stats
    print("\n📊 VECTOR INDEX STATS:")
    stats = vector_service.get_index_stats()
    print(f"   Total vectors: {stats.get('total_vectors', 0)}")
    print(f"   Dimension: {stats.get('dimension', 0)}")
    print(f"   Index fullness: {stats.get('index_fullness', 0.0)}")
    
    # Test 2: Try a simple search without filters first
    print("\n🎯 BASIC SEARCH (no filters):")
    
    try:
        # Search without any filters to see what's in there
        results = vector_service.index.query(
            vector=vector_service.generate_embedding("test"),
            top_k=5,
            include_metadata=True
        )
        
        print(f"   Found {len(results.matches)} vectors:")
        for i, match in enumerate(results.matches, 1):
            print(f"     {i}. Vector ID: {match.id}")
            print(f"        Score: {match.score:.3f}")
            print(f"        Metadata keys: {list(match.metadata.keys())}")
            if 'campaign_id' in match.metadata:
                print(f"        Campaign ID: {match.metadata['campaign_id']}")
            if 'content_type' in match.metadata:
                print(f"        Content Type: {match.metadata['content_type']}")
            if 'title' in match.metadata:
                print(f"        Title: {match.metadata['title']}")
            print()
            
    except Exception as e:
        print(f"   ❌ Basic search failed: {e}")
    
    # Test 3: Search with campaign filter
    print("\n🎯 CAMPAIGN-FILTERED SEARCH:")
    
    try:
        results = vector_service.index.query(
            vector=vector_service.generate_embedding("test"),
            top_k=5,
            include_metadata=True,
            filter={"campaign_id": campaign_id}
        )
        
        print(f"   Found {len(results.matches)} vectors for campaign {campaign_id}:")
        for i, match in enumerate(results.matches, 1):
            print(f"     {i}. Vector ID: {match.id}")
            print(f"        Score: {match.score:.3f}")
            print(f"        Metadata: {match.metadata}")
            print()
            
    except Exception as e:
        print(f"   ❌ Campaign search failed: {e}")

def test_robust_semantic_search(campaign_id: str):
    """Test semantic search with error handling for missing metadata"""
    
    print(f"\n🎯 ROBUST SEMANTIC SEARCH FOR CAMPAIGN: {campaign_id}")
    print("="*60)
    
    vector_service = VectorService(debug=True)
    
    test_queries = [
        "magic",
        "gods",
        "cities", 
        "politics",
        "threats",
        "geography"
    ]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        
        try:
            # Generate query embedding
            query_embedding = vector_service.generate_embedding(query)
            
            # Search with campaign filter
            results = vector_service.index.query(
                vector=query_embedding,
                top_k=3,
                include_metadata=True,
                filter={"campaign_id": campaign_id}
            )
            
            if results.matches:
                for i, match in enumerate(results.matches, 1):
                    print(f"     {i}. Score: {match.score:.3f}")
                    print(f"        Vector ID: {match.id}")
                    
                    # Safely extract metadata
                    metadata = match.metadata
                    content_type = metadata.get('content_type', 'unknown')
                    title = metadata.get('title', 'No title')
                    text_snippet = metadata.get('text_snippet', 'No snippet')
                    
                    print(f"        Type: {content_type}")
                    print(f"        Title: {title}")
                    print(f"        Snippet: {text_snippet[:100]}...")
                    print()
            else:
                print("     No results found")
                
        except Exception as e:
            print(f"     ❌ Search failed: {e}")

def main():
    """Main test function"""
    print("🌍 CONTEXT RETRIEVAL TESTER")
    print("="*60)
    
    # List available campaigns
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT c.campaign_id, c.name, w.world_name, w.created_at
            FROM campaigns c
            LEFT JOIN worlds w ON c.campaign_id = w.campaign_id
            WHERE w.world_id IS NOT NULL
            ORDER BY w.created_at DESC
            LIMIT 5
        """)
        
        campaigns = cur.fetchall()
        
        if campaigns:
            print("🌍 CAMPAIGNS WITH WORLDS:")
            print("="*50)
            for i, (campaign_id, name, world_name, created_at) in enumerate(campaigns, 1):
                print(f"   {i}. Campaign: {name}")
                print(f"      World: {world_name}")
                print(f"      ID: {campaign_id}")
                print(f"      Created: {created_at}")
                print("      " + "-"*40)
        else:
            print("❌ No campaigns with worlds found. Create a world first!")
            return
            
    except Exception as e:
        print(f"❌ Error listing campaigns: {e}")
        return
    finally:
        cur.close()
        conn.close()
    
    # Use the most recent campaign for testing
    campaign_id, name, world_name, created_at = campaigns[0]
    print(f"\n🎯 Testing with most recent campaign: {name} ({world_name})")
    
    # Run the exploration tests
    explore_vector_database(campaign_id)
    test_robust_semantic_search(campaign_id)

if __name__ == "__main__":
    main()