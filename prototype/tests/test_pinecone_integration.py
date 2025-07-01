#!/usr/bin/env python3
"""
Test script to demonstrate Pinecone integration with world building.

This script shows the complete workflow:
1. Create a test campaign
2. Generate world content 
3. Save to PostgreSQL + create embeddings in Pinecone
4. Perform semantic searches
5. Show how AI agents can retrieve context

Run this after setting up your Pinecone credentials in .env
"""

import json
from db import db
from services.vector_service import VectorService

def test_pinecone_integration():
    """Test the complete Pinecone integration workflow"""
    print("🧪 TESTING PINECONE INTEGRATION")
    print("="*50)
    
    try:
        # Step 1: Create test campaign and user
        print("\n1️⃣ Setting up test campaign...")
        user_id = db.get_or_create_user("test_user")
        campaign_id = db.create_campaign("Pinecone Test Campaign", "Testing vector integration", user_id)
        print(f"✅ Created campaign: {campaign_id}")
        
        # Step 2: Create sample world data
        print("\n2️⃣ Creating sample world data...")
        sample_world_data = {
            "world_info": {
                "world_name": "Vectoria",
                "world_description": "Vectoria is a mystical realm where magic flows through crystalline networks beneath the earth. The ancient Embedding Stones channel raw magical energy into spells, creating a world where knowledge itself has power. Scholars and wizards study in the Great Library of Dimensions, where each book contains not just words, but compressed understanding that can be instantly accessed through magical resonance.",
                "theme_list": "magic, knowledge, crystals, libraries",
                "theme_description": "A world where information and magic are intertwined"
            },
            "magic_system": {
                "magic_level": "High",
                "commonality": "Magic is as common as books in Vectoria. Every settlement has multiple spellcasters.",
                "mechanics": "Magic in Vectoria works through semantic resonance. Spells are cast by speaking concepts that resonate with the Embedding Stones buried deep underground. The more precise and nuanced the magical language, the more powerful the effect.",
                "limitations": "Overuse of complex magical concepts can lead to 'semantic exhaustion' where the caster temporarily loses the ability to access certain spell concepts."
            },
            "pantheon": {
                "structure": "The gods of Vectoria are embodiments of different types of knowledge and understanding.",
                "major_deities": [
                    "Lexica, Goddess of Language and Communication",
                    "Algorithmus, God of Logic and Mathematics", 
                    "Memoria, Goddess of Memory and Archives"
                ]
            },
            "global_threats": [{
                "primary_threat": "The Corruption of the Word Weaver",
                "threat_details": "An ancient entity known as the Word Weaver has begun corrupting the magical language itself. Where it passes, spells fail, books become unreadable, and the very concept of meaning breaks down. It seeks to reduce all communication to meaningless noise.",
                "world_impact": "Towns affected by the Word Weaver experience communication breakdowns, failed magic, and growing paranoia as people can no longer trust that their words mean what they intend."
            }],
            "size": {
                "scope": "regional",
                "region_count": 2,
                "major_city_count": 3,
                "settlement_count": 12
            }
        }
        
        # Step 3: Save world to database (this will also create embeddings)
        print("\n3️⃣ Saving world to database + creating embeddings...")
        world_id = db.save_world(campaign_id, sample_world_data)
        print(f"✅ World saved with ID: {world_id}")
        
        # Step 4: Test vector service directly
        print("\n4️⃣ Testing vector service stats...")
        vector_service = VectorService()
        stats = vector_service.get_index_stats()
        print(f"📊 Pinecone Index Stats: {stats}")
        
        # Step 5: Test semantic search
        print("\n5️⃣ Testing semantic searches...")
        
        test_queries = [
            "What happens when magic fails?",
            "Tell me about the libraries and books",
            "What are the gods like?",
            "Ancient threats and corruption",
            "How does spellcasting work?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = db.search_world_content(campaign_id, query, limit=3)
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']} (Score: {result['similarity_score']:.3f})")
                print(f"      Type: {result['content_type']}")
                print(f"      Preview: {result['text_snippet'][:100]}...")
        
        # Step 6: Show how this helps AI agents
        print("\n6️⃣ AI Agent Context Retrieval Example...")
        player_question = "I want to cast a spell but I'm worried about the risks"
        
        print(f"\n🤖 Player asks: '{player_question}'")
        print("🧠 AI searches world knowledge...")
        
        context_results = db.search_world_content(
            campaign_id, 
            "magic risks limitations spell casting dangers", 
            content_types=["magic_system"],
            limit=2
        )
        
        print("\n📚 Retrieved Context for AI:")
        for result in context_results:
            print(f"   📖 {result['title']}")
            print(f"   📝 {result['content'][:200]}...")
            print()
        
        print("✅ AI can now respond with accurate world-specific information!")
        
        # Step 7: Cleanup
        print("\n7️⃣ Cleaning up test data...")
        try:
            # Use the regular database delete which will cascade
            conn = db.get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM campaigns WHERE campaign_id = %s", (campaign_id,))
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Test campaign deleted")
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup failed: {cleanup_error}")
            print("   Note: You may need to manually clean up test data")
        
        print("\n🎉 PINECONE INTEGRATION TEST COMPLETE!")
        print("✅ World content → PostgreSQL → Pinecone → Semantic Search → AI Context")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_search_only():
    """Quick test of search functionality on existing data"""
    print("🔍 TESTING SEARCH ON EXISTING DATA")
    print("="*40)
    
    try:
        # Get any existing campaign
        campaigns = db.list_campaigns()
        if not campaigns:
            print("❌ No existing campaigns found. Run test_pinecone_integration() first.")
            return
        
        campaign_id = campaigns[0][0]  # Use first campaign
        campaign_name = campaigns[0][1]
        
        print(f"🎯 Searching in campaign: {campaign_name}")
        
        test_query = input("\n🔍 Enter your search query: ").strip()
        if not test_query:
            test_query = "magic"
        
        results = db.search_world_content(campaign_id, test_query)
        
        if results:
            print(f"\n📚 Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']} (Score: {result['similarity_score']:.3f})")
                print(f"   Type: {result['content_type']}")
                print(f"   Preview: {result['text_snippet'][:150]}...")
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        test_search_only()
    else:
        print("🚀 Choose test mode:")
        print("1. Full integration test (creates test data)")
        print("2. Search existing data")
        
        choice = input("\nEnter choice (1/2): ").strip()
        
        if choice == "2":
            test_search_only()
        else:
            test_pinecone_integration() 