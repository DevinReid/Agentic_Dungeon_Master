# utils/command_handler.py
import cli
from db.db import get_recent_events, get_npc_relationships, get_npcs_at_location

class CommandHandler:
    def __init__(self, game_session=None, combat_manager=None):
        self.game_session = game_session
        self.combat_manager = combat_manager
    
    def handle_command(self, command, context="story"):
        """
        Handle global commands like 'menu', 'win', etc.
        
        Args:
            command: The command string (like "menu", "win")
            context: Either "story" or "combat" for context-specific behavior
            
        Returns:
            True if command was handled, False if it's a normal action
        """
        cmd = command.strip().lower()
        
        if cmd == "menu":
            return self.handle_menu(context)
        elif cmd == "win":
            return self.handle_win()
        elif cmd == "god":
            return self.handle_god_mode()
        elif cmd == "heal":
            return self.handle_heal()
        elif cmd == "debug":
            return self.handle_debug_info()
        elif cmd == "memory":
            return self.handle_memory()
        elif cmd == "relationships" or cmd == "relations":
            return self.handle_relationships()
        elif cmd == "npcs":
            return self.handle_npcs()
        elif cmd == "location":
            return self.handle_location()
        elif cmd == "help":
            return self.handle_help()
        # Easy to add more commands here
        
        return False  # Not a command, treat as normal action
    
    def handle_menu(self, context):
        """Handle menu command - different behavior for story vs combat"""
        if context == "combat":
            while True:
                choice = cli.ui_player_choice()
                if choice == "Character Sheet":
                    cli.ui_character_sheet()
                elif choice in ["Inventory (placeholder)", "Journal (placeholder)"]:
                    cli.typer.echo(f"{choice} shown here (placeholder)")
                elif choice == "Return to Start Menu":
                    cli.ui_main_menu()
                elif choice == "Quit Application":
                    cli.ui_quit()
                elif choice == "Type an Action":
                    break
            return True
        else:
            return "exit_to_menu"
    
    def handle_win(self):
        """Debug command: Kill all enemies instantly"""
        if self.combat_manager:
            print("🎯 DEBUG: Killing all enemies...")
            for name, npc in self.combat_manager.combatants.items():
                if name != "player":
                    npc["hp"] = 0
            print("All enemies defeated!")
            return True
        else:
            print("Win command only works in combat!")
            return True
    
    def handle_god_mode(self):
        """Debug command: Max health and AC"""
        if self.game_session:
            print("🛡️ DEBUG: God mode activated!")
            self.game_session.character["hp"] = 999
            self.game_session.character["ac"] = 25
            if self.combat_manager:
                self.combat_manager.combatants["player"]["hp"] = 999
                self.combat_manager.combatants["player"]["ac"] = 25
            return True
        return True
    
    def handle_heal(self):
        """Debug command: Full heal"""
        if self.game_session:
            print("💚 DEBUG: Full heal!")
            max_hp = self.game_session.character.get("max_hp", 100)
            self.game_session.character["hp"] = max_hp
            if self.combat_manager:
                self.combat_manager.combatants["player"]["hp"] = max_hp
            return True
        return True
    
    def handle_debug_info(self):
        """Debug command: Show current state"""
        print("🔍 DEBUG INFO:")
        if self.game_session:
            print(f"Campaign: {self.game_session.campaign_id}")
            print(f"User: {self.game_session.username}")
            print(f"Character ID: {self.game_session.character_id}")
            print(f"Character: {self.game_session.character}")
        if self.combat_manager:
            print(f"Combat: {self.combat_manager.combatants}")
        return True

    def handle_help(self):
        """Show available commands"""
        print("\n🎮 AVAILABLE COMMANDS:")
        print("Debug Commands:")
        print("  god     - God mode (999 HP, 25 AC)")
        print("  heal    - Full heal")
        print("  win     - Kill all enemies (combat only)")
        print("  debug   - Show debug info")
        print("  menu    - Return to menu")
        print("\n🧠 AI Memory Commands:")
        print("  memory       - View recent story events")
        print("  relationships - View NPC relationships")
        print("  npcs         - View NPCs at current location")
        print("  location     - View current location")
        print("  help         - Show this help")
        print("\nType any command during story or combat!")
        return True

    def handle_memory(self):
        """View recent story events from AI memory"""
        if not self.game_session:
            print("❌ No game session active")
            return True
            
        print("\n🧠 AI MEMORY - RECENT EVENTS:")
        events = get_recent_events(self.game_session.campaign_id, limit=8)
        
        if not events:
            print("   No events recorded yet.")
            return True
            
        for i, event in enumerate(events, 1):
            timestamp = event['created_at'].strftime("%H:%M:%S") if event['created_at'] else "Unknown"
            print(f"\n{i}. [{timestamp}] {event['event_type'].upper()}")
            print(f"   Location: {event['location'] or 'Unknown'}")
            print(f"   Event: {event['description'][:100]}{'...' if len(event['description']) > 100 else ''}")
            if event['player_actions']:
                print(f"   Player: {event['player_actions'][:80]}{'...' if len(event['player_actions']) > 80 else ''}")
                
        return True

    def handle_relationships(self):
        """View NPC relationships"""
        if not self.game_session or not self.game_session.character_id:
            print("❌ No game session or character active")
            return True
            
        print(f"\n🤝 NPC RELATIONSHIPS for {self.game_session.player_name}:")
        relationships = get_npc_relationships(self.game_session.campaign_id, self.game_session.character_id)
        
        if not relationships:
            print("   No relationships established yet.")
            return True
            
        for rel in relationships:
            score = rel['relationship_score']
            
            # Determine relationship status
            if score > 50:
                status = "🟢 Strong Ally"
            elif score > 20:
                status = "🔵 Ally"
            elif score > -20:
                status = "⚪ Neutral"
            elif score > -50:
                status = "🔴 Enemy"
            else:
                status = "🔴 Strong Enemy"
                
            print(f"\n• {rel['npc_name']} - {status} ({score:+d})")
            if rel['last_interaction']:
                print(f"  Last: {rel['last_interaction'][:100]}{'...' if len(rel['last_interaction']) > 100 else ''}")
            
            # Show relationship history if available
            if rel['history'] and len(rel['history'].strip()) > 0:
                history_lines = rel['history'].split('\n')[-2:]  # Last 2 interactions
                for line in history_lines:
                    if line.strip():
                        print(f"  History: {line.strip()[:80]}{'...' if len(line.strip()) > 80 else ''}")
                        
        return True

    def handle_npcs(self):
        """View NPCs at current location"""
        if not self.game_session:
            print("❌ No game session active")
            return True
            
        location = self.game_session.current_location
        print(f"\n👥 NPCs AT {location.upper()}:")
        
        npcs = get_npcs_at_location(self.game_session.campaign_id, location, status="alive")
        
        if not npcs:
            print("   No living NPCs at this location.")
            return True
            
        for npc in npcs:
            disposition_emoji = {
                "friendly": "😊",
                "hostile": "😠", 
                "neutral": "😐",
                "unknown": "❓"
            }.get(npc.get('disposition', 'neutral'), "😐")
            
            print(f"\n• {npc['name']} ({npc['class']}) {disposition_emoji}")
            print(f"  HP: {npc['hp']}/{npc.get('max_hp', npc['hp'])} | AC: {npc['ac']} | Status: {npc['status']}")
            if npc.get('backstory'):
                print(f"  Background: {npc['backstory'][:100]}{'...' if len(npc['backstory']) > 100 else ''}")
            
            last_seen = npc.get('last_seen')
            if last_seen:
                print(f"  Last seen: {last_seen.strftime('%Y-%m-%d %H:%M:%S') if hasattr(last_seen, 'strftime') else last_seen}")
                
        return True

    def handle_location(self):
        """View current location information"""
        if not self.game_session:
            print("❌ No game session active")
            return True
            
        location = self.game_session.current_location
        print(f"\n📍 CURRENT LOCATION: {location}")
        
        # Count NPCs at this location
        npcs = get_npcs_at_location(self.game_session.campaign_id, location, status="alive")
        dead_npcs = get_npcs_at_location(self.game_session.campaign_id, location, status="dead")
        
        print(f"   Living NPCs: {len(npcs)}")
        if dead_npcs:
            print(f"   Dead NPCs: {len(dead_npcs)}")
            
        # Show recent events at this location
        all_events = get_recent_events(self.game_session.campaign_id, limit=20)
        location_events = [e for e in all_events if e.get('location') == location]
        
        if location_events:
            print(f"   Recent events here: {len(location_events)}")
            latest = location_events[0]
            print(f"   Latest: {latest['event_type']} - {latest['description'][:80]}{'...' if len(latest['description']) > 80 else ''}")
            
        return True