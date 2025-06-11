from bots.npc_creator_agent import NpcCreatorAgent

test_context_2 = """
    Foo, the battle-hardened Fighter whose name carries weight in taverns and war camps alike, stands at the edge of a crumbling trade road deep within the Hinterwood. The path, once used by merchants and travelers, now lies silent beneath the creeping vines and twisted branches of the cursed trees. You’ve tracked the rumors of missing caravans and stolen goods to this forsaken stretch of woodland, where the stench of blood and rust clings to the wind.

    As you tighten your grip on your weapon, you catch the faint sound of squabbling just beyond the treeline. Then—snap! A branch breaks under a careless foot. A group of goblins emerge from the brush, crude blades in hand, their yellow eyes gleaming with mischief and malice. One bares jagged teeth in a grin, while the other circles around, looking for an opening.
"""

known_characters = "Foo"

npc_creator = NpcCreatorAgent()
list_of_characters = npc_creator.generate_character_sheet(description=test_context_2, player_character_names=known_characters)

print(list_of_characters)