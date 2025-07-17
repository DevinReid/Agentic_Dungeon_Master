from npc import NPC

first_npc = NPC(
    name="Gandalf",
    character_class="Wizard",
    level=20,
    hp=100,
    max_hp=100,
    ac=10,
    strength=10,
)

print(first_npc)

print(first_npc.name)

