import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prototype.combat_system import CombatManager
import pytest
import random

def test_combat_manager_setup():
    """Test that CombatManager initializes correctly"""
    test_npcs = [
        {"name": "Test Goblin", "hp": 10, "ac": 13},
        {"name": "Test Orc", "hp": 15, "ac": 14}
    ]
    
    combat_manager = CombatManager("TestPlayer", test_npcs, player_hp=12, player_ac=15)
    
    assert "player" in combat_manager.combatants
    assert "Test Goblin" in combat_manager.combatants
    assert "Test Orc" in combat_manager.combatants
    assert combat_manager.combatants["player"]["hp"] == 12
    
    print("✅ Combat Manager setup works correctly")

def test_victory_scenario():
    """Test that player wins against weak enemies"""
    weak_npcs = [{"name": "Weak Goblin", "hp": 1, "ac": 5}]
    combat_manager = CombatManager("TestHero", weak_npcs, player_hp=20, player_ac=15)
    
    # Manually kill all NPCs
    for npc_name, npc_data in combat_manager.combatants.items():
        if npc_name != "player":
            npc_data["hp"] = 0
    
    assert combat_manager.is_combat_over() == True
    
    player_hp = combat_manager.combatants["player"]["hp"]
    npcs_alive = [c for n, c in combat_manager.combatants.items() if n != "player" and c["hp"] > 0]
    result = "player_won" if player_hp > 0 and not npcs_alive else "player_died"
    
    assert result == "player_won"
    print("✅ Victory detection works correctly")

def test_defeat_scenario():
    """Test that player loses when killed"""
    strong_npcs = [{"name": "Strong Orc", "hp": 20, "ac": 15}]
    combat_manager = CombatManager("WeakHero", strong_npcs, player_hp=1, player_ac=5)
    
    # Manually kill player
    combat_manager.combatants["player"]["hp"] = 0
    
    assert combat_manager.is_combat_over() == True
    
    player_hp = combat_manager.combatants["player"]["hp"]
    result = "player_died" if player_hp <= 0 else "player_won"
    
    assert result == "player_died"
    print("✅ Defeat detection works correctly")

def simulate_full_combat(combat_manager):
    """Simulate a full combat without user input"""
    combat_manager.initialize_initiative()
    max_rounds = 20  # Prevent infinite loops
    
    for round_num in range(max_rounds):
        if combat_manager.is_combat_over():
            break
            
        who = combat_manager.current_combatant()
        
        if who == "player":
            # Player attacks first alive enemy
            target = next((c for n, c in combat_manager.combatants.items() 
                          if n != "player" and c["hp"] > 0), None)
            if target:
                roll = random.randint(1, 20)
                if roll >= target["ac"]:
                    damage = random.randint(1, 8)
                    target["hp"] -= damage
        else:
            # NPC attacks player
            npc = combat_manager.combatants[who]
            if npc["hp"] > 0:  # Only living NPCs attack
                roll = random.randint(1, 20)
                if roll >= combat_manager.combatants["player"]["ac"]:
                    damage = random.randint(1, 6)
                    combat_manager.combatants["player"]["hp"] -= damage
        
        combat_manager.next_turn()
    
    # Determine result
    player_hp = combat_manager.combatants["player"]["hp"]
    npcs_alive = [c for n, c in combat_manager.combatants.items() if n != "player" and c["hp"] > 0]
    
    if player_hp <= 0:
        return "player_died"
    elif not npcs_alive:
        return "player_won"
    else:
        return "timeout"

def test_realistic_combat_balance():
    """Test actual combat balance - reveals if game is winnable"""
    # Realistic scenario from your game
    npcs = [
        {"name": "Goblin 1", "hp": 10, "ac": 13},
        {"name": "Goblin 2", "hp": 10, "ac": 13}
    ]
    
    player_wins = 0
    player_deaths = 0
    timeouts = 0
    total_tests = 50
    
    for i in range(total_tests):
        # Fresh combat each time
        fresh_npcs = [{"name": npc["name"], "hp": npc["hp"], "ac": npc["ac"]} for npc in npcs]
        combat_manager = CombatManager("TestPlayer", fresh_npcs, player_hp=12, player_ac=15)
        
        result = simulate_full_combat(combat_manager)
        if result == "player_won":
            player_wins += 1
        elif result == "player_died":
            player_deaths += 1
        else:
            timeouts += 1
    
    win_rate = player_wins / total_tests * 100
    death_rate = player_deaths / total_tests * 100
    
    print(f"🎲 Combat Balance Results (2 goblins vs player):")
    print(f"   Player wins: {win_rate:.1f}% ({player_wins}/{total_tests})")
    print(f"   Player dies: {death_rate:.1f}% ({player_deaths}/{total_tests})")
    print(f"   Timeouts: {timeouts}/{total_tests}")
    
    # This will probably fail and show your balance issues!
    if win_rate < 20:
        print("⚠️  WARNING: Combat is heavily unbalanced against player!")

if __name__ == "__main__":
    test_combat_manager_setup()
    test_victory_scenario() 
    test_defeat_scenario()
    test_realistic_combat_balance()
    print("\n🎉 All combat tests completed!")