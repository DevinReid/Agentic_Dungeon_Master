#!/usr/bin/env python3
"""
Stress Test for Entity Extraction Pipeline

Tests the limits of our entity extraction system with progressively complex content.
Validates the 4000 token limit solution and identifies practical extraction limits.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import json
import time
from bots.entity_extractor_agent import EntityExtractorAgent

def generate_complex_content(complexity_level="medium"):
    """Generate increasingly complex content for stress testing"""
    
    base_content = {
        "simple": """
        The wizard Gandalf lives in the Tower of Magic. 
        He owns a powerful staff called Lightbringer.
        The nearby village of Hobbiton is peaceful.
        """,
        
        "medium": """
        In the vast realm of Aethermoor, the Council of Mages convenes at the Ivory Citadel every full moon. 
        The council consists of five powerful wizards: Archmage Valdris the Wise, Sorceress Lyralei of the Silver Flame, 
        Warlock Thane Blackwood, Enchantress Melody Starwhisper, and the mysterious Void Walker known only as Shadow.
        
        The Ivory Citadel stands atop Mount Crystalspire, overlooking the trading port of Goldenhaven. 
        Within its walls lies the legendary Codex of Eternal Wisdom, guarded by the ancient dragon Pyraxis.
        
        The neighboring kingdoms of Nordhelm and Sunward Isle have formed an alliance called the Golden Accord 
        to protect against the growing threat of the Shadowlands, where the Lich King Malachar rules from 
        his fortress of Bone and Shadow.
        """,
        
        "high": """
        The continent of Valdoran is a sprawling tapestry of kingdoms, each with its own rich history and complex politics. 
        The Northern Reaches are dominated by the Kingdom of Frostguard, ruled by Queen Elara Ironwill from her 
        crystal palace in the capital city of Rimeheart. Her court consists of the skilled diplomat Lord Gareth Stormwind, 
        the master spy Lady Raven Nightshade, and the legendary knight Sir Marcus Goldenblade.
        
        To the east lies the Merchant Republic of Goldspire, governed by the Trade Council of Seven, including 
        Guildmaster Thornwick Coinweaver, Admiral Seraphina Tidecaller, and the shrewd negotiator Baron Aldric Silvertongue.
        
        The central regions are home to the Arcane Academy of Stellarwind, where Archmage Celestine Moonwhisper 
        trains the next generation of spellcasters. The academy's Great Library houses the Tome of Infinite Possibilities, 
        the Staff of Stellar Convergence, and the mysterious Orb of Temporal Echoes.
        
        In the southern deserts, the Nomad Tribes of the Singing Sands follow the ancient traditions, led by 
        Chieftain Zara Sandstorm and her council of elders. They worship the Sun God Solaris at the Temple of 
        Golden Dunes and seek the lost city of Mirajeth, said to contain the Fountain of Eternal Youth.
        
        The western coastlands are plagued by the Pirate Confederation, led by the notorious Captain Blackheart, 
        whose fleet includes the dreadnought "Crimson Revenge" and the swift corsair "Ghostwind's Gambit."
        
        Ancient evils stir in the Shadowlands, where the Cult of the Void Eye serves the demon lord Morghast 
        from their stronghold in the Obsidian Towers. They seek the Three Seals of Binding to release their 
        master from his eternal prison.
        """,
        
        "extreme": """
        The multiverse of Omnirealm encompasses seventeen distinct planes of existence, each teeming with unique 
        civilizations, magical phenomena, and cosmic threats that challenge the very fabric of reality itself.
        
        The Prime Material Plane centers around the world of Aethermoor, where the Celestial Empire of Draconis 
        spans twelve provinces, each governed by a Council of Nobles: Duke Alderon Dragonheart of Flamereach, 
        Duchess Valeria Stormcrest of Thunderpeak, Count Thaddeus Ironforge of Steelholm, Baroness Lyanna Rosethorne 
        of Bloomfield, Lord Commander Gareth Wolfsong of Ironhold, Lady Magistrate Seraphina Goldleaf of Sunhaven, 
        Marquis Damien Shadowbane of Nightfall, Earl Roderick Stonehammer of Greymont, Countess Evangeline Brightwater 
        of Crystalmeadow, Baron Maximilian Swiftarrow of Greenwood, Duchess Cordelia Frostborn of Icehaven, 
        and the mysterious Archon Vex of the Void Reaches.
        
        The Plane of Eternal Fire houses the Salamander Kingdoms, where Fire Lord Pyrotheus the Magnificent 
        rules from his Molten Throne, commanding legions of flame elementals, phoenix riders, and the elite 
        Infernal Guard. His court includes the sorceress Ignia Blazeheart, the smith-god Vulcan Forgemaster, 
        and the warrior princess Ember Dragonscale.
        
        In the Shadowfell, the Necropolis of Eternal Night serves as the capital of the Undead Dominion, 
        where Lich Emperor Malachar commands an army of death knights, bone dragons, and spectral legions. 
        His inner circle consists of the vampire lord Dracul Bloodmoon, the banshee queen Morgana Soulrender, 
        the death knight Ser Blackheart, and the lich sorceress Vex'ahlia Deathwhisper.
        
        The Feywild blooms with the Court of Eternal Spring, ruled by Queen Titania Starweaver and King Oberon 
        Moonwhisper, whose subjects include the mischievous pixie lord Puck Glimmerwing, the wise dryad 
        Willow Oaksong, the fierce satyr warrior Pan Stormhoof, and the enigmatic eladrin archfey Autumn Twilight.
        
        The Astral Plane serves as the domain of the Githyanki Empire, where the legendary Lich Queen Vlaakith 
        commands her Silver Sword legions from the fortress-city of Tu'narath. Her generals include the 
        supreme commander Zerthimon Planeslicer, the void captain Gith'tya Starrender, and the psychic warrior 
        Xen'drik Mindbreaker.
        
        Ancient artifacts of immense power are scattered across the planes: the Crown of Infinite Dominion, 
        the Blade of Reality's Edge, the Orb of Planar Convergence, the Staff of Cosmic Manipulation, 
        the Amulet of Temporal Mastery, the Gauntlets of Dimensional Binding, the Boots of Ethereal Walking, 
        the Cloak of Astral Shadows, the Ring of Elemental Command, the Scepter of Divine Authority, 
        the Tome of Universal Truths, the Chalice of Eternal Life, the Mirror of Infinite Possibilities, 
        the Harp of Celestial Harmony, and the legendary Sword of Omnipotence.
        
        The organization known as the Planar Concordat works to maintain balance across the multiverse, 
        with members including the archpaladin Aurelius Lightbringer, the sage Minerva Truthseeker, 
        the ranger captain Artemis Wildstrider, the monk grandmaster Kenjiro Zenmaster, the bard diplomat 
        Melody Songweaver, the rogue spymaster Shadowfox, and the mysterious warlock known only as the 
        Void Walker.
        
        Cosmic threats emerge from the Far Realm, where the aberration lord Cthulhu'thep seeks to consume 
        reality itself, aided by his cultists in the Order of the Writhing Darkness, including the mad 
        prophet Xanathar Tentaclemouth, the mind flayer elder brain Illithidor, and the beholder tyrant 
        Gazorthak the All-Seeing.
        """
    }
    
    return base_content.get(complexity_level, base_content["medium"])

def measure_token_usage(text):
    """Rough estimate of token usage (1 token ≈ 4 characters for GPT models)"""
    return len(text) // 4

def test_progressive_complexity():
    """Test entity extraction with progressively complex content"""
    
    print("🚀 STRESS TEST: Progressive Complexity")
    print("=" * 60)
    
    complexity_levels = ["simple", "medium", "high", "extreme"]
    results = []
    
    for level in complexity_levels:
        print(f"\n📊 Testing {level.upper()} complexity...")
        print("-" * 40)
        
        content = generate_complex_content(level)
        word_count = len(content.split())
        estimated_tokens = measure_token_usage(content)
        
        print(f"📖 Content: {word_count} words, ~{estimated_tokens} tokens")
        
        test_campaign_id = str(uuid.uuid4())
        existing_tags = ["stress_test", level, "complexity"]
        
        try:
            start_time = time.time()
            
            extractor = EntityExtractorAgent(debug=True)
            extracted_entities = extractor.extract_entities(
                content=content,
                content_type="stress_test",
                existing_tags=existing_tags,
                campaign_id=test_campaign_id
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Count total entities
            total_entities = sum(len(entities) for entities in extracted_entities.values())
            entity_types = len(extracted_entities.keys())
            
            result = {
                'level': level,
                'word_count': word_count,
                'estimated_tokens': estimated_tokens,
                'processing_time': processing_time,
                'total_entities': total_entities,
                'entity_types': entity_types,
                'success': True,
                'entity_breakdown': {k: len(v) for k, v in extracted_entities.items()}
            }
            
            print(f"✅ Success: {total_entities} entities in {processing_time:.2f}s")
            print(f"   Entity types: {entity_types}")
            print(f"   Breakdown: {result['entity_breakdown']}")
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            result = {
                'level': level,
                'word_count': word_count,
                'estimated_tokens': estimated_tokens,
                'processing_time': None,
                'total_entities': 0,
                'entity_types': 0,
                'success': False,
                'error': str(e)
            }
            results.append(result)
    
    # Summary
    print(f"\n📋 PROGRESSIVE COMPLEXITY RESULTS")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{result['level'].upper():8} | {result['word_count']:4} words | {result['estimated_tokens']:4} tokens | {status}")
        if result['success']:
            print(f"         | {result['total_entities']:3} entities | {result['processing_time']:5.2f}s")
        else:
            print(f"         | Error: {result.get('error', 'Unknown')}")
    
    return results

def test_token_limit_boundary():
    """Test content that approaches and exceeds typical token limits"""
    
    print(f"\n🎯 STRESS TEST: Token Limit Boundary")
    print("=" * 60)
    
    # Create content that tests specific token ranges
    test_cases = [
        ("800_tokens", "Content designed to use ~800 tokens", generate_token_targeted_content(800)),
        ("1500_tokens", "Content designed to use ~1500 tokens", generate_token_targeted_content(1500)),
        ("3000_tokens", "Content designed to use ~3000 tokens", generate_token_targeted_content(3000)),
        ("4000_tokens", "Content designed to use ~4000 tokens", generate_token_targeted_content(4000)),
        ("5000_tokens", "Content designed to use ~5000 tokens", generate_token_targeted_content(5000)),
    ]
    
    results = []
    
    for test_name, description, content in test_cases:
        print(f"\n🔍 Testing {test_name}...")
        print(f"   {description}")
        
        estimated_tokens = measure_token_usage(content)
        word_count = len(content.split())
        
        print(f"   Content: {word_count} words, ~{estimated_tokens} tokens")
        
        test_campaign_id = str(uuid.uuid4())
        existing_tags = ["stress_test", "token_limit", test_name]
        
        try:
            start_time = time.time()
            
            extractor = EntityExtractorAgent(debug=True)
            extracted_entities = extractor.extract_entities(
                content=content,
                content_type="token_limit_test",
                existing_tags=existing_tags,
                campaign_id=test_campaign_id
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            total_entities = sum(len(entities) for entities in extracted_entities.values())
            
            result = {
                'test_name': test_name,
                'estimated_tokens': estimated_tokens,
                'word_count': word_count,
                'processing_time': processing_time,
                'total_entities': total_entities,
                'success': True
            }
            
            print(f"   ✅ Success: {total_entities} entities in {processing_time:.2f}s")
            results.append(result)
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            result = {
                'test_name': test_name,
                'estimated_tokens': estimated_tokens,
                'word_count': word_count,
                'processing_time': None,
                'total_entities': 0,
                'success': False,
                'error': str(e)
            }
            results.append(result)
    
    # Summary
    print(f"\n📋 TOKEN LIMIT BOUNDARY RESULTS")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{result['test_name']:12} | {result['estimated_tokens']:4} tokens | {status}")
        if result['success']:
            print(f"               | {result['total_entities']:3} entities | {result['processing_time']:5.2f}s")
        else:
            print(f"               | Error: {result.get('error', 'Unknown')}")
    
    return results

def generate_token_targeted_content(target_tokens):
    """Generate content targeting a specific token count"""
    
    # Base template that we'll expand
    base_template = """
    The realm of {realm_name} is a vast and complex domain ruled by {ruler_name} from the {capital_city}.
    
    The nobility includes {noble_list}.
    
    Important locations within the realm include {location_list}.
    
    The military forces consist of {military_list}.
    
    Ancient artifacts of power include {artifact_list}.
    
    The realm faces threats from {threat_list}.
    
    Religious orders operating in the realm include {religious_list}.
    
    Trade guilds and organizations include {guild_list}.
    """
    
    # Calculate how much content we need to reach target tokens
    base_tokens = measure_token_usage(base_template)
    needed_tokens = target_tokens - base_tokens
    
    if needed_tokens <= 0:
        return base_template.format(
            realm_name="Valdoran",
            ruler_name="King Aldric the Wise",
            capital_city="Golden Citadel",
            noble_list="Duke Gareth and Duchess Lyanna",
            location_list="the Silver Mountains and Whispering Woods",
            military_list="the Royal Guard and Knights of the Silver Rose",
            artifact_list="the Crown of Ages and the Sword of Truth",
            threat_list="bandits and wild monsters",
            religious_list="the Order of Light",
            guild_list="the Merchants' Alliance"
        )
    
    # Generate expanded content to reach target tokens
    expanded_content = generate_expanded_content(needed_tokens)
    
    return base_template.format(
        realm_name="Valdoran",
        ruler_name="King Aldric the Wise",
        capital_city="Golden Citadel of Eternal Radiance",
        noble_list=expanded_content["nobles"],
        location_list=expanded_content["locations"],
        military_list=expanded_content["military"],
        artifact_list=expanded_content["artifacts"],
        threat_list=expanded_content["threats"],
        religious_list=expanded_content["religious"],
        guild_list=expanded_content["guilds"]
    )

def generate_expanded_content(token_budget):
    """Generate expanded content lists within a token budget"""
    
    content_templates = {
        "nobles": [
            "Duke Gareth Stormwind of the Northern Reaches",
            "Duchess Lyanna Moonwhisper of the Silverleaf Domain",
            "Count Thaddeus Ironforge of the Mountain Holds",
            "Baroness Seraphina Goldleaf of the Sunward Territories",
            "Lord Commander Marcus Dragonheart of the Eastern Marches",
            "Lady Magistrate Cordelia Frostborn of the Winter Lands",
            "Marquis Damien Shadowbane of the Darkwood Realm",
            "Earl Roderick Stonehammer of the Granite Peaks",
            "Countess Evangeline Brightwater of the Crystal Lakes",
            "Baron Maximilian Swiftarrow of the Greenwood Expanse"
        ],
        "locations": [
            "the Crystalline Peaks where ancient dragons slumber",
            "the Whispering Woods home to elven enchanters",
            "the Shadowmere Marshlands ruled by hag covens",
            "the Golden Plains where centaur tribes roam",
            "the Frostguard Mountains with their dwarven citadels",
            "the Sunward Archipelago of trading ports",
            "the Darkwood Forest concealing ancient ruins",
            "the Silverleaf Valley of mystical gardens",
            "the Stormwind Cliffs overlooking the Sea of Storms",
            "the Ironforge Caverns filled with precious metals"
        ],
        "military": [
            "the Royal Guard of the Golden Lion",
            "the Knights of the Silver Rose",
            "the Stormwind Cavalry",
            "the Ironforge Defenders",
            "the Shadowbane Rangers",
            "the Dragonheart Elite Guard",
            "the Frostborn Mountain Guards",
            "the Brightwater Naval Fleet",
            "the Swiftarrow Archers",
            "the Stonehammer Heavy Infantry"
        ],
        "artifacts": [
            "the Crown of Eternal Dominion",
            "the Blade of Reality's Edge",
            "the Orb of Planar Convergence",
            "the Staff of Cosmic Manipulation",
            "the Amulet of Temporal Mastery",
            "the Gauntlets of Dimensional Binding",
            "the Boots of Ethereal Walking",
            "the Cloak of Astral Shadows",
            "the Ring of Elemental Command",
            "the Scepter of Divine Authority"
        ],
        "threats": [
            "the Lich King Malachar and his undead legions",
            "the Dragon Cult of the Crimson Scale",
            "the Demon Lord Baphomet's cultists",
            "the Orc Warlord Gruumsh's hordes",
            "the Aberration Entity from the Far Realm",
            "the Vampire Lord Dracul's blood court",
            "the Mind Flayer colony in the Underdark",
            "the Beholder Tyrant Gazorthak's domain",
            "the Fiendish Duke Asmodeus's servants",
            "the Elemental Chaos threatening reality"
        ],
        "religious": [
            "the Order of the Radiant Dawn",
            "the Temple of Eternal Light",
            "the Monastery of Silent Contemplation",
            "the Clerics of the Healing Spring",
            "the Paladins of Justice",
            "the Druids of the Ancient Grove",
            "the Priests of the Storm God",
            "the Shamans of the Earth Mother",
            "the Oracles of Prophetic Vision",
            "the Guardians of Sacred Knowledge"
        ],
        "guilds": [
            "the Merchants' Alliance of Golden Commerce",
            "the Artisans' Brotherhood of Master Crafters",
            "the Thieves' Guild of Silent Shadows",
            "the Assassins' Order of the Crimson Blade",
            "the Scholars' Circle of Infinite Wisdom",
            "the Healers' Covenant of Merciful Hearts",
            "the Explorers' Society of Distant Lands",
            "the Performers' Troupe of Enchanted Arts",
            "the Alchemists' Union of Mystical Formulas",
            "the Enchanters' Guild of Magical Artifice"
        ]
    }
    
    # Distribute token budget across categories
    categories = list(content_templates.keys())
    tokens_per_category = token_budget // len(categories)
    
    result = {}
    
    for category in categories:
        items = []
        current_tokens = 0
        
        for template in content_templates[category]:
            item_tokens = measure_token_usage(template)
            if current_tokens + item_tokens <= tokens_per_category:
                items.append(template)
                current_tokens += item_tokens
            else:
                break
        
        result[category] = ", ".join(items)
    
    return result

def run_stress_tests():
    """Run all stress tests and provide comprehensive results"""
    
    print("🧪 ENTITY EXTRACTION STRESS TEST SUITE")
    print("=" * 60)
    print("Testing the limits of our entity extraction pipeline")
    print("Validating 4000 token limit solution")
    print("=" * 60)
    
    # Run all stress tests
    progressive_results = test_progressive_complexity()
    token_limit_results = test_token_limit_boundary()
    
    # Overall summary
    print(f"\n🎯 OVERALL STRESS TEST RESULTS")
    print("=" * 60)
    
    total_tests = len(progressive_results) + len(token_limit_results)
    successful_tests = (
        sum(1 for r in progressive_results if r['success']) +
        sum(1 for r in token_limit_results if r['success'])
    )
    
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {(successful_tests / total_tests * 100):.1f}%")
    
    # Find the practical limits
    max_successful_tokens = 0
    for result in progressive_results + token_limit_results:
        if result['success']:
            estimated_tokens = result.get('estimated_tokens', 0)
            if estimated_tokens > max_successful_tokens:
                max_successful_tokens = estimated_tokens
    
    print(f"\nPractical token limit: ~{max_successful_tokens} tokens")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 60)
    
    if successful_tests == total_tests:
        print("✅ All tests passed! The 4000 token limit appears effective.")
        print("✅ No batching features needed at this time.")
    elif max_successful_tokens < 4000:
        print(f"⚠️  Issues found below 4000 tokens (max successful: {max_successful_tokens})")
        print("⚠️  Consider investigating other limiting factors.")
    else:
        print("✅ 4000 token limit is working well.")
        print("💡 Consider implementing batching for content >4000 tokens.")
    
    return {
        'progressive_results': progressive_results,
        'token_limit_results': token_limit_results,
        'success_rate': successful_tests / total_tests,
        'max_successful_tokens': max_successful_tokens
    }

if __name__ == "__main__":
    results = run_stress_tests()
