# game_session.py
import cli
from bots.story_agent import StoryAgent
from db.db import (create_character, get_character_in_campaign, update_character_stats,
                   save_npc, get_npcs_at_location, save_event, get_recent_events, 
                   update_npc_relationship, get_npc_relationships, get_or_create_user,
                   clear_characters_in_campaign)
from bots.combat_agent import CombatAgent
from services.combat_system import CombatManager, analyze_combat_state_ai
from utils.dice_utility import DiceUtility
from utils.debug_util import debug_log
from bots.npc_creator_agent import NpcCreatorAgent
import json

class GameSession:
    def __init__(self, campaign_id, username):
        self.dice = DiceUtility()
        self.story = StoryAgent()
        self.npc_creator = NpcCreatorAgent()
        self.combat_agent = CombatAgent()
        
        # Campaign and user context
        self.campaign_id = campaign_id
        self.username = username
        self.user_id = get_or_create_user(username)
        
        # Game state
        self.session_context = ""
        self.last_dm_text = ""
        self.player_name = ""
        self.player_class = ""
        self.in_combat = False
        self.character = {}
        self.character_id = None
        self.current_npc_list = []
        self.current_location = "Starting Area"
        
        print(f"🎮 Game session initialized for campaign {str(campaign_id)[:8]}... (user: {username})")
        
        # Try to load existing character
        self.load_character_stats()

    def setup_character(self, name, char_class):
        debug_log("setup_character() called.")
        self.player_name = name
        self.player_class = char_class
        
        # Clear any existing characters in this campaign for this user (for testing)
        existing_char = get_character_in_campaign(self.campaign_id, self.user_id)
        if existing_char:
            clear_characters_in_campaign(self.campaign_id)
        
        # Create new character
        hp = 30
        self.character_id = create_character(self.campaign_id, self.user_id, name, char_class, hp)
        
        # Generate stats
        stats = self.story.generate_stats(char_class, 1)
        stats["ac"] = stats["ac"] + 2
        stats["hp"] = stats["hp"] + 50
        stats["max_hp"] = stats["hp"]
        
        # Update character with generated stats
        update_character_stats(self.character_id, stats)
        self.load_character_stats()

    def run_intro_scene(self):
        debug_log("run_intro_scene() called.")
        intro = self.story.generate_intro(self.player_class, self.player_name)
        self.session_context += f"\nDM: {intro['content']}"
        self.last_dm_text = intro["content"]

        # 🧠 AI MEMORY: Check for existing NPCs at this location first
        existing_npcs = get_npcs_at_location(self.campaign_id, self.current_location, status="alive")
        
        if existing_npcs:
            print(f"\n🧠 Found {len(existing_npcs)} existing NPCs at {self.current_location}")
            self.current_npcs = existing_npcs
            
            # Get their relationship history for context
            if self.character_id:
                relationships = get_npc_relationships(self.campaign_id, self.character_id)
                if relationships:
                    relationship_context = self._build_relationship_context(relationships)
                    print(f"📜 Relationship context: {relationship_context}")
        else:
            print(f"\n🆕 Generating new NPCs for {self.current_location}")
            # Generate new NPCs and save them to database
            generated_npcs = self.npc_creator.generate_character_sheet(
                description=intro["content"], 
                player_character_names=[self.player_name]
            )
            
            # Save NPCs to database for persistence
            for npc in generated_npcs:
                npc_id = save_npc(self.campaign_id, npc, self.current_location)
                npc["npc_id"] = npc_id
                print(f"💾 Saved NPC: {npc['name']} ({npc['class']}) to database")
            
            self.current_npcs = generated_npcs

        # 🧠 AI MEMORY: Save the intro as a story event
        npc_names = [npc["name"] for npc in self.current_npcs] if self.current_npcs else []
        character_ids = [self.character_id] if self.character_id else []
        
        save_event(
            self.campaign_id,
            event_type="intro",
            description=intro["content"],
            location_name=self.current_location,
            npcs_involved=json.dumps(npc_names),
            character_ids=json.dumps(character_ids),
            player_actions="Started new adventure",
            session_context=self.session_context
        )
        
        return intro["content"]

    def action_handler(self, action):
        # Check for commands first
        from utils.command_handler import CommandHandler
        cmd_handler = CommandHandler(game_session=self)
        command_result = cmd_handler.handle_command(action, context="story")
        
        if command_result == "exit_to_menu":
            return "exit_to_menu"  # Signal to exit to campaign menu
        elif command_result is True:
            return "command_handled"  # Command was handled, continue game
        
        # 🧠 AI MEMORY: Get recent events for context
        recent_events = get_recent_events(self.campaign_id, limit=5)
        relationships = []
        if self.character_id:
            relationships = get_npc_relationships(self.campaign_id, self.character_id)
        
        # Check for combat first
        combat_triggered = analyze_combat_state_ai(self.last_dm_text, action)
        if combat_triggered:
            return "combat"

        # Handle dice rolling as before
        roll_info = self.dice.analyze_for_roll(self.last_dm_text, action)
        if roll_info.get('roll_needed'):
            result = self.dice.roll_dice(roll_info['dice_type'])
            cli.ui_handle_dice_roll(roll_info, result)
            success = self.dice.determine_success(roll_info, result)
            cli.ui_declare_dice_result(success)
        else:
            success = "No result required"

        # 🧠 AI MEMORY: Enhanced story generation with persistent context
        response_json = self._enhanced_story_generation(
            action, roll_info, success, recent_events, relationships
        )
        
        new_dm_text = response_json["content"]
        self.session_context += f"\nPlayer: {action}\nDM: {new_dm_text}"
        self.last_dm_text = new_dm_text
        
        # 🧠 AI MEMORY: Save this interaction as an event
        npc_names = [npc["name"] for npc in self.current_npcs] if self.current_npcs else []
        character_ids = [self.character_id] if self.character_id else []
        
        save_event(
            self.campaign_id,
            event_type="interaction",
            description=new_dm_text,
            location_name=self.current_location,
            npcs_involved=json.dumps(npc_names),
            character_ids=json.dumps(character_ids),
            player_actions=action,
            consequences=success,
            session_context=self.session_context
        )
        
        # 🧠 AI MEMORY: Update NPC relationships based on the interaction
        if self.character_id:
            self._update_relationships_from_interaction(action, new_dm_text)
        
        return new_dm_text

    def _enhanced_story_generation(self, action, roll_info, success, recent_events, relationships):
        """Enhanced story generation with persistent world context"""
        
        # Build context from persistent data
        context_additions = []
        
        if recent_events:
            context_additions.append("RECENT EVENTS:")
            for event in recent_events[:3]:  # Last 3 events
                context_additions.append(f"- {event['event_type']}: {event['description'][:100]}...")
        
        if relationships:
            context_additions.append("\nNPC RELATIONSHIPS:")
            for rel in relationships[:5]:  # Top 5 relationships
                score_desc = "ally" if rel['relationship_score'] > 20 else "enemy" if rel['relationship_score'] < -20 else "neutral"
                context_additions.append(f"- {rel['npc_name']}: {score_desc} ({rel['relationship_score']})")
        
        if self.current_npcs:
            context_additions.append(f"\nCURRENT NPCs AT {self.current_location}:")
            for npc in self.current_npcs:
                context_additions.append(f"- {npc['name']} ({npc['class']}) - {npc.get('disposition', 'neutral')}")
        
        enhanced_context = self.session_context
        if context_additions:
            enhanced_context += "\n\n--- AI MEMORY CONTEXT ---\n" + "\n".join(context_additions) + "\n--- END CONTEXT ---\n"
        
        return self.story.story_agent(
            enhanced_context, action,
            roll_info.get('roll_needed'),
            roll_info.get('roll_type'),
            roll_info.get('dc'),
            success
        )

    def _update_relationships_from_interaction(self, player_action, dm_response):
        """Analyze interaction and update NPC relationships"""
        # Simple heuristic - you could make this more sophisticated with AI analysis
        positive_words = ["help", "save", "protect", "kind", "generous", "thank"]
        negative_words = ["attack", "threaten", "steal", "harm", "insult", "kill"]
        
        combined_text = f"{player_action} {dm_response}".lower()
        
        relationship_change = 0
        interaction_desc = f"Player: {player_action}"
        
        # Simple sentiment analysis
        positive_count = sum(1 for word in positive_words if word in combined_text)
        negative_count = sum(1 for word in negative_words if word in combined_text)
        
        if positive_count > negative_count:
            relationship_change = positive_count * 5  # +5 per positive word
        elif negative_count > positive_count:
            relationship_change = negative_count * -10  # -10 per negative word
        
        # Update relationships for all current NPCs
        if relationship_change != 0 and self.current_npcs:
            for npc in self.current_npcs:
                update_npc_relationship(self.campaign_id, npc["name"], self.character_id, relationship_change, interaction_desc)
                print(f"📊 Updated relationship with {npc['name']}: {relationship_change:+d}")

    def _build_relationship_context(self, relationships):
        """Build a summary of NPC relationships for AI context"""
        if not relationships:
            return "No previous relationships established."
        
        context_parts = []
        for rel in relationships[:3]:  # Top 3 most recent
            score = rel['relationship_score']
            if score > 20:
                desc = f"{rel['npc_name']} is your ally"
            elif score < -20:
                desc = f"{rel['npc_name']} is hostile towards you"
            else:
                desc = f"{rel['npc_name']} is neutral"
            
            if rel['last_interaction']:
                desc += f" (last: {rel['last_interaction'][:50]}...)"
            context_parts.append(desc)
        
        return "; ".join(context_parts)

    def start_combat(self, npc_names=None):
        if self.current_npcs:
            npcs = [{"name": npc["name"], "hp": npc["hp"], "ac": npc["ac"]} 
                    for npc in self.current_npcs]
        else:
            # Fallback to hard-coded if no NPCs generated
            npcs = [{"name": name, "hp": 10, "ac": 13} for name in (npc_names or [])]
            
        self.combat_manager = CombatManager(
                player_name=self.player_name, 
                npcs=npcs, 
                player_hp=self.character["hp"], 
                player_ac=self.character["ac"]
            )   
        self.combat_manager.initialize_initiative()
        self.combat_manager.current_turn_index = 0
        self.combat_manager.round = 1

        result = self.combat_manager.run_combat()
        if result == "exit_to_menu":
            return "exit_to_menu"  # Propagate exit signal
        elif result == "player_died":
            return self.handle_player_death()
        elif result == "player_won":
            return self.handle_victory()

    def load_character_stats(self):
        character = get_character_in_campaign(self.campaign_id, self.user_id)
        if character:
            self.character = character
            self.character_id = character["character_id"]
            self.player_name = character["name"]
            self.player_class = character["class"]
            
            # Add combat AC boost
            self.character["ac"] += 2
        else:
            self.character = {}
            self.character_id = None

    def handle_player_death(self):
        print("Your adventure has come to an end...")
        print("Returning to main menu.")
        
        # Clear session data for clean restart
        self.current_npcs = []
        self.session_context = ""
        self.last_dm_text = ""
        self.in_combat = False
        
        return "game_over" 
    
    def handle_victory(self):
        print("\n🎉 VICTORY! 🎉")
        print("You have defeated your enemies!")
        
        # Clear the NPCs since they're dead
        self.current_npcs = []
        
        # Generate post-combat story continuation
        post_combat_story = self.story.story_agent(
            self.session_context, 
            "I have won the battle", 
            False, None, None, "Victory achieved"
        )
        
        # Update context and continue story
        self.session_context += f"\nPlayer: [Combat Victory]\nDM: {post_combat_story['content']}"
        self.last_dm_text = post_combat_story['content']
        
        return post_combat_story['content']