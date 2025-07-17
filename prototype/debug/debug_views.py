import typer
from db.db import get_recent_events, get_npc_relationships, get_npcs_at_location

class DebugViews:
    def __init__(self, game_session=None, combat_manager=None):
        self.game_session = game_session
        self.combat_manager = combat_manager

    def show_memory_events(self):
        if not self.game_session:
            typer.secho("No game session found", fg=typer.colors.RED)
            return
        
        typer.secho("\n🧠 Ai Memory - recent events:", fg=typer.colors.CYAN, bold=True)
        events = get_recent_events(self.game_session.campaign_id, limit=10)
        if not events:
            typer.secho("No recent events found", fg=typer.colors.RED)
            return
        
        for i, event in enumerate(events, 1):
            timestamp = event['created_at'].strftime('%Y-%m-%d %H:%M:%S') if event['created_at'] else "Unknown"
            typer.echo(f"\n{i}. [{timestamp}] {event['event_type'].upper()}")           
            typer.echo(f"   Location: {event['location'] or 'Unknown'}")
            typer.echo(f"   Event: {event['description'][:100]}{'...' if len(event['description']) > 100 else ''}")
            if event['player_actions']:
                typer.echo(f"   Player: {event['player_actions'][:80]}{'...' if len(event['player_actions']) > 80 else ''}")
        
        input("\n📖 Press Enter to continue...")

    def show_npcs_at_location(self):
        """Display NPCs at current location"""
        if not self.game_session:
            typer.secho("❌ No game session active", fg=typer.colors.RED)
            return
            
        location = self.game_session.current_location
        typer.secho(f"\n👥 NPCs AT {location.upper()}:", fg=typer.colors.CYAN, bold=True)
        
        npcs = get_npcs_at_location(self.game_session.campaign_id, location, status="alive")
        
        if not npcs:
            typer.echo("   No living NPCs at this location.")
            input("\n📖 Press Enter to continue...")
            return
            
        for npc in npcs:
            disposition_emoji = {
                "friendly": "😊",
                "hostile": "😠", 
                "neutral": "😐",
                "unknown": "❓"
            }.get(npc.get('disposition', 'neutral'), "😐")
            
            typer.echo(f"\n• {npc['name']} ({npc['class']}) {disposition_emoji}")
            typer.echo(f"  HP: {npc['hp']}/{npc.get('max_hp', npc['hp'])} | AC: {npc['ac']} | Status: {npc['status']}")
            if npc.get('backstory'):
                typer.echo(f"  Background: {npc['backstory'][:100]}{'...' if len(npc['backstory']) > 100 else ''}")
                
        input("\n📖 Press Enter to continue...")

    def show_relationships(self):
        """Display NPC relationships"""
        if not self.game_session or not self.game_session.character_id:
            typer.secho("❌ No game session or character active", fg=typer.colors.RED)
            return
            
        typer.secho(f"\n🤝 NPC RELATIONSHIPS for {self.game_session.player_name}:", fg=typer.colors.CYAN, bold=True)
        relationships = get_npc_relationships(self.game_session.campaign_id, self.game_session.character_id)
        
        if not relationships:
            typer.echo("   No relationships established yet.")
            input("\n📖 Press Enter to continue...")
            return
            
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
                
            typer.echo(f"\n• {rel['npc_name']} - {status} ({score:+d})")
            if rel['last_interaction']:
                typer.echo(f"  Last: {rel['last_interaction'][:100]}{'...' if len(rel['last_interaction']) > 100 else ''}")
                
        input("\n📖 Press Enter to continue...")

    def show_location_info(self):
        """Display current location information"""
        if not self.game_session:
            typer.secho("❌ No game session active", fg=typer.colors.RED)
            return
            
        location = self.game_session.current_location
        typer.secho(f"\n📍 CURRENT LOCATION: {location}", fg=typer.colors.CYAN, bold=True)
        
        # Count NPCs at this location
        npcs = get_npcs_at_location(self.game_session.campaign_id, location, status="alive")
        dead_npcs = get_npcs_at_location(self.game_session.campaign_id, location, status="dead")
        
        typer.echo(f"   Living NPCs: {len(npcs)}")
        if dead_npcs:
            typer.echo(f"   Dead NPCs: {len(dead_npcs)}")
            
        # Show recent events at this location
        all_events = get_recent_events(self.game_session.campaign_id, limit=20)
        location_events = [e for e in all_events if e.get('location') == location]
        
        if location_events:
            typer.echo(f"   Recent events here: {len(location_events)}")
            latest = location_events[0]
            typer.echo(f"   Latest: {latest['event_type']} - {latest['description'][:80]}{'...' if len(latest['description']) > 80 else ''}")
            
        input("\n📖 Press Enter to continue...")

    def show_character_stats(self):
        """Display character statistics"""
        if not self.game_session:
            typer.secho("❌ No game session active", fg=typer.colors.RED)
            return
            
        char = self.game_session.character
        typer.secho("\n🎲 CHARACTER STATS:", fg=typer.colors.CYAN, bold=True)
        typer.echo(f"Campaign ID: {self.game_session.campaign_id}")
        typer.echo(f"Character ID: {self.game_session.character_id}")
        typer.echo(f"Name: {char.get('name', 'Unknown')}")
        typer.echo(f"Class: {char.get('class', 'Unknown')}")
        typer.echo(f"Level: {char.get('level', 1)}")
        typer.echo(f"Experience: {char.get('experience', 0)}")
        typer.echo(f"HP: {char.get('hp', 0)}/{char.get('max_hp', 0)}")
        typer.echo(f"AC: {char.get('ac', 10)}")
        typer.echo(f"STR: {char.get('strength', 10)}  DEX: {char.get('dexterity', 10)}  CON: {char.get('constitution', 10)}")
        typer.echo(f"INT: {char.get('intelligence', 10)}  WIS: {char.get('wisdom', 10)}  CHA: {char.get('charisma', 10)}")
        
        input("\n📖 Press Enter to continue...")

    def show_campaign_analytics(self):
        """Display campaign analytics and statistics"""
        if not self.game_session:
            typer.secho("❌ No game session active", fg=typer.colors.RED)
            return
            
        typer.secho("\n📊 CAMPAIGN ANALYTICS:", fg=typer.colors.CYAN, bold=True)
        typer.echo("🚧 Coming soon - will show:")
        typer.echo("  • Total play time")
        typer.echo("  • Events by type")
        typer.echo("  • NPCs created/killed")
        typer.echo("  • Locations visited")
        typer.echo("  • Relationship changes over time")
        
        input("\n📖 Press Enter to continue...")

    # Placeholder methods for raw data viewing
    def show_raw_campaign_data(self):
        typer.echo("🚧 Raw campaign data viewer - coming soon!")
        input("\n📖 Press Enter to continue...")

    def show_raw_character_data(self):
        typer.echo("🚧 Raw character data viewer - coming soon!")
        input("\n📖 Press Enter to continue...")

    def show_raw_location_data(self):
        typer.echo("🚧 Raw location data viewer - coming soon!")
        input("\n📖 Press Enter to continue...")

    def show_raw_event_history(self):
        typer.echo("🚧 Raw event history viewer - coming soon!")
        input("\n📖 Press Enter to continue...")

    def show_bot_states(self):
        typer.echo("🚧 Bot states viewer - coming soon!")
        input("\n📖 Press Enter to continue...")