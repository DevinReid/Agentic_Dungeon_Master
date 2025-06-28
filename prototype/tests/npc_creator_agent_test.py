from bots.npc_creator_agent import NpcCreatorAgent
import pytest
import json

wizard_context = """
    In the mystical realm of Eldoria, Foo, a gifted Wizard of unparalleled repute, finds themselves embroiled in a dire quest.
    The Kingdom of Eldoria is under threat from an ancient malevolence, as the Empress of Shadows rises, casting her dark influence across the lands.
    Having heeded the call for aid, Foo has journeyed to the heart of the Whispering Woods, where the last known fragment of the fabled Lightstone is said to reside.
    This powerful artifact is believed to hold the key to vanquishing the Empress once and for all.
    As Foo navigates deeper into the tangled woodland, the air grows thin and an oppressive aura settles around them.
    Suddenly, twisted creatures of shadow leap from the surrounding thickets, their eyes gleaming with malicious intent.
    Will Foo harness the arcane energies at their disposal to fend off this sinister pack?
"""

warrior_context = """
    Foo, the battle-hardened Fighter whose name carries weight in taverns and war camps alike, stands at the edge of a crumbling trade road deep within the Hinterwood.
    The path, once used by merchants and travelers, now lies silent beneath the creeping vines and twisted branches of the cursed trees.
    You’ve tracked the rumors of missing caravans and stolen goods to this forsaken stretch of woodland, where the stench of blood and rust clings to the wind.

    As you tighten your grip on your weapon, you catch the faint sound of squabbling just beyond the treeline.
    Then—snap! A branch breaks under a careless foot.
    A group of goblins emerge from the brush, crude blades in hand, their yellow eyes gleaming with mischief and malice.
    One bares jagged teeth in a grin, while the other circles around, looking for an opening.
"""

warrior_named_char_context = """
    Foo, the battle-hardened Fighter whose name carries weight in taverns and war camps alike, stands at the edge of a crumbling trade road deep within the Hinterwood.
    The path, once used by merchants and travelers, now lies silent beneath the creeping vines and twisted branches of the cursed trees.
    You’ve tracked the rumors of missing caravans and stolen goods to this forsaken stretch of woodland, where the stench of blood and rust clings to the wind.

    As you tighten your grip on your weapon, you catch the faint sound of squabbling just beyond the treeline.
    Then—snap! A branch breaks under a careless foot.
    Two goblins, Peach and Parrot, emerge from the brush, crude blades in hand, their yellow eyes gleaming with mischief and malice.
    One bares jagged teeth in a grin, while the other circles around, looking for an opening.
"""

known_characters = ["Foo"]

npc_creator = NpcCreatorAgent()

def test_wizard_length(): 
    list_of_characters = npc_creator.generate_character_sheet(description=wizard_context, player_character_names=known_characters)
    print_character_sheets(list_of_characters)
    assert len(list_of_characters) > 1

def test_warrior_length():
    list_of_characters = npc_creator.generate_character_sheet(description=warrior_context, player_character_names=known_characters)
    print_character_sheets(list_of_characters)
    assert len(list_of_characters) > 1

def test_warrior_name():
    list_of_characters = npc_creator.generate_character_sheet(description=warrior_named_char_context, player_character_names=known_characters)
    first_character_json = list_of_characters[0]
    print_character_sheets(list_of_characters)
    assert first_character_json["name"] == "Peach" or first_character_json["name"] == "Parrot"

def print_character_sheets(characters):
    for i, char in enumerate(characters, 1):
        print(f"\n--- Character {i} ---")
        print(f"Name: {char['name']}")
        print(f"Class: {char['class']}")
        print(f"Level: {char['level']} | HP: {char['hp']} | AC: {char['ac']}")
        print(f"STR: {char['strength']} | DEX: {char['dexterity']} | CON: {char['constitution']}")
        print(f"INT: {char['intelligence']} | WIS: {char['wisdom']} | CHA: {char['charisma']}")
        print(f"ID: {char['id']}")



### TEST NOTES ###

"""
EDGE CASE NOTE - Background vs Present NPCs Issue
=====================================================

PROBLEM DISCOVERED: The NPC Creator picks up ALL mentioned characters, 
not just those present in the immediate scene.

EXAMPLE FROM GAMEPLAY:
Story: "...whispers speak of a rogue sorcerer tampering with forbidden spells... 
an animated book, fierce and powerful, leaps from the shelves and lunges toward him"

Generated NPCs: ["Sorcerer", "Book 1"] 
Expected NPCs: ["Book 1"] only

ISSUE: The "rogue sorcerer" is background lore (not present), but "animated book" 
is the actual immediate threat. Combat should only include present enemies.

POTENTIAL SOLUTIONS TO TEST LATER:
1. Update system prompt to focus on "currently present" vs "mentioned" NPCs
2. Look for action verbs (attacks, leaps, emerges) vs passive mentions
3. Add combat-specific NPC extraction that filters for immediate threats
4. Create test cases with mixed present/absent NPCs

TODO: Add test cases like:
- Story mentions past villain + present monster -> should only get present monster
- Story with multiple present enemies -> should get all present
- Story with only background NPCs -> should return empty list

This affects combat balance since background NPCs shouldn't participate in fights.
"""

"""
EDGE CASE NOTE - Allegiance/Friend vs Foe Issue
==============================================

PROBLEM DISCOVERED: NPC Creator generates ALL characters but Combat System 
treats ALL NPCs as enemies fighting the player.

EXAMPLE FROM GAMEPLAY:
Story: "...goblins attack while townspeople cower..."
Generated NPCs: ["goblin 1", "goblin 2", "goblin leader", "townsperson 1", "townsperson 2"]
Combat Result: ALL 5 NPCs attack the player (townspeople attacking player!)

ISSUE: No distinction between:
- Enemies (goblins should attack player)
- Allies (townspeople should help player or stay neutral)
- Neutrals (bystanders who shouldn't participate)

SYMPTOMS:
- Friendly NPCs dealing damage to player
- Combat becomes unbalanced (too many enemies)
- Narratively nonsensical (why are civilians attacking?)

POTENTIAL SOLUTIONS TO IMPLEMENT LATER:
1. Add allegiance field to NPC generation: "enemy"/"ally"/"neutral"
2. Filter NPCs in combat - only include hostile creatures
3. Update NPC Creator prompt to specify combat participants vs background characters
4. Create separate methods: generate_enemies() vs generate_all_npcs()
5. Combat system checks allegiance before adding to enemy list

TODO: Add test cases for:
- Mixed enemy/ally scenarios -> should separate properly
- Pure ally scenarios -> should not trigger combat
- Neutral bystanders -> should not participate in combat

This significantly affects game balance and narrative coherence.
"""