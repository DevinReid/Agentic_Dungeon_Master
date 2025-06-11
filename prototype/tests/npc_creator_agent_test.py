from prototype.bots.npc_creator_agent import NpcCreatorAgent
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
    Two goblins, Peaches and Parrot, emerge from the brush, crude blades in hand, their yellow eyes gleaming with mischief and malice.
    One bares jagged teeth in a grin, while the other circles around, looking for an opening.
"""

known_characters = ["Foo"]

npc_creator = NpcCreatorAgent()

def test_wizard_length(): 
    list_of_characters = npc_creator.generate_character_sheet(description=wizard_context, player_character_names=known_characters)
    print(list_of_characters)
    assert len(list_of_characters) > 1

def test_warrior_length():
    list_of_characters = npc_creator.generate_character_sheet(description=warrior_context, player_character_names=known_characters)
    print(list_of_characters)
    assert len(list_of_characters) > 1

def test_warrior_name():
    list_of_characters = npc_creator.generate_character_sheet(description=warrior_named_char_context, player_character_names=known_characters)
    first_character_json = list_of_characters[0]
    assert first_character_json["name"] == "Peaches" or first_character_json["name"] == "Parrot"