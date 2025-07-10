#!/usr/bin/env python3
"""
Super simple query test - just change the query and run!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vector_service import VectorService

# CAMPAIGN ID - don't change this
CAMPAIGN_ID = "e23f1a62-6092-4e41-a903-edf08c26a552"

# CHANGE THIS QUERY TO TEST DIFFERENT SEARCHES
QUERY = "Where is the nearest mountain?"

def simple_query():
    """Simple query test"""
    print(f"🔍 Query: '{QUERY}'")
    print(f"🎯 Campaign: {CAMPAIGN_ID}")
    print("="*50)
    
    vector_service = VectorService()
    
    # Generate query embedding
    query_embedding = vector_service.generate_embedding(QUERY)
    
    # Search with campaign filter
    results = vector_service.index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        filter={"campaign_id": CAMPAIGN_ID}
    )
    
    if results.matches:
        print(f"✅ Found {len(results.matches)} results:")
        for i, match in enumerate(results.matches, 1):
            print(f"\n{i}. Score: {match.score:.3f}")
            print(f"   Type: {match.metadata.get('content_type', 'unknown')}")
            print(f"   Snippet: {match.metadata.get('text_snippet', 'No snippet')[:200]}...")
    else:
        print("❌ No results found")

if __name__ == "__main__":
    simple_query() 