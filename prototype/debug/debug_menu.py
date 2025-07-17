
from InquirerPy import inquirer
from .debug_views import DebugViews
from .debug_util import DebugUtils

class DebugMenu:
    def __init__(self, game_session=None, combat_manager=None):
        self.game_session = game_session
        self.combat_manager = combat_manager
        self.views = DebugViews(game_session, combat_manager)
        self.utils = DebugUtils(game_session, combat_manager)

    def show_main_debug_menu(self):
        while True:
            choice = inquirer.select(
                message = "Debug Menu - choose an option:",
                choices = [
                    "🧠 View Memory/Events",
                    "👥 NPCs at Location", 
                    "🤝 Relationship Status",
                    "📍 Location Info",
                    "🎲 Character Stats",
                    "🗄️ Raw Data Viewer",
                    "⚙️ God Mode Tools",
                    "📊 Campaign Analytics",
                    "🔙 Back to Game"
                ]
            ).execute()
            
            if choice == "🧠 View Memory/Events":
                self.views.show_memory_events()
            elif choice == "👥 NPCs at Location":
                self.views.show_npcs_at_location()
            elif choice == "🤝 Relationship Status":
                self.views.show_relationships()
            elif choice == "📍 Location Info":
                self.views.show_location_info()
            elif choice == "🎲 Character Stats":
                self.views.show_character_stats()
            elif choice == "🗄️ Raw Data Viewer":
                self.show_raw_data_menu()
            elif choice == "⚙️ God Mode Tools":
                self.show_god_mode_menu()
            elif choice == "📊 Campaign Analytics":
                self.views.show_campaign_analytics()
            elif choice == "🔙 Back to Game":
                break

    def show_raw_data_menu(self):
           
        """Submenu for raw data viewing"""
        choice = inquirer.select(
                message="🗄️ Raw Data Viewer - Choose data type:",
                choices=[
                    "🎭 Campaign Data",
                    "👤 Character Data", 
                    "🏰 Location Data",
                    "📜 Event History",
                    "🤖 Bot States",
                    "🔙 Back to Debug Menu"
                ]
            ).execute()
            
        if choice == "🎭 Campaign Data":
            self.views.show_raw_campaign_data()
        elif choice == "👤 Character Data":
            self.views.show_raw_character_data()
        elif choice == "🏰 Location Data":
            self.views.show_raw_location_data()
        elif choice == "📜 Event History":
            self.views.show_raw_event_history()
        elif choice == "🤖 Bot States":
            self.views.show_bot_states()
        # Back option handled by returning

        
    def show_god_mode_menu(self):
        """Submenu for god mode/cheat tools"""
        choice = inquirer.select(
            message="⚙️ God Mode Tools - Choose an option:",
            choices=[
                "🛡️ God Mode (999 HP, 25 AC)",
                "💚 Full Heal",
                "🎯 Kill All Enemies",
                "💰 Add Gold/Items",
                "📈 Level Up",
                "🔙 Back to Debug Menu"
            ]
        ).execute()
        
        if choice == "🛡️ God Mode (999 HP, 25 AC)":
            self.utils.activate_god_mode()
        elif choice == "💚 Full Heal":
            self.utils.full_heal()
        elif choice == "🎯 Kill All Enemies":
            self.utils.kill_all_enemies()
        elif choice == "💰 Add Gold/Items":
            self.utils.add_resources()
        elif choice == "📈 Level Up":
            self.utils.level_up_character()
        # Back option handled by returning