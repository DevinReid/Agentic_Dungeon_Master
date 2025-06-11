from bots.npc_creator_agent import NpcCreatorAgent

test_context_2 = """
    In the mystical realm of Eldoria, Foo, a gifted Wizard of unparalleled repute, finds themselves embroiled in a dire quest.
    The Kingdom of Eldoria is under threat from an ancient malevolence, as the Empress of Shadows rises, casting her dark influence across the lands.
    Having heeded the call for aid, Foo has journeyed to the heart of the Whispering Woods, where the last known fragment of the fabled Lightstone is said to reside.
    This powerful artifact is believed to hold the key to vanquishing the Empress once and for all.
    As Foo navigates deeper into the tangled woodland, the air grows thin and an oppressive aura settles around them.
    Suddenly, twisted creatures of shadow leap from the surrounding thickets, their eyes gleaming with malicious intent.
    Will Foo harness the arcane energies at their disposal to fend off this sinister pack?
"""

known_characters = "Foo"

npc_creator = NpcCreatorAgent()
list_of_characters = npc_creator.generate_character_sheet(description=test_context_2, player_character_names=known_characters)

print(list_of_characters)