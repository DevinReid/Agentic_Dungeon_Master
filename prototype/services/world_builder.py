#!/usr/bin/env python3
"""
World Builder Orchestrator

Simple phase coordinator for world generation.
Calls different AI bots in sequence and handles results.
Does NOT assign values itself - lets the AI determine structure.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from cli import WorldBuilderCLI
from db.db import create_world_record
from bots.content_processor_agent import ContentProcessorAgent
# Import the actual builders
from bots.world_builder.universe_builder import UniverseBuilder
from bots.world_builder.regional_builder import RegionalBuilder  


@dataclass
class WorldGenerationResult:
    """Result container for world generation operations"""
    success: bool
    world_name: str = ""
    world_data: Dict = None
    regions: List[Dict] = None
    settlements: List[Dict] = None 
    npcs: List[Dict] = None
    conflicts: List[Dict] = None
    quests: List[Dict] = None
    error: str = ""

class WorldGenerationOrchestrator:
    """Phase coordinator for world generation - calls different bots in sequence"""
    
    def __init__(self):
        
        self.universe_builder = UniverseBuilder()
        self.regional_builder = RegionalBuilder()
        
        # TODO: Initialize these when they're implemented
        # self.settlement_builder = SettlementBuilder()
        # self.npc_builder = NPCNetworkBuilder()
        # self.conflict_builder = ConflictBuilder()
        # self.quest_builder = QuestNetworkBuilder()

    def world_creation__campaign_menu(self, campaign_id, campaign_name):
        """Handle world creation choice for a new campaign"""
        from InquirerPy import inquirer
        
        print(f"\n🌍 WORLD SETUP FOR CAMPAIGN: {campaign_name}")
        print("="*60)
        
        world_choice = inquirer.select(
            message="What kind of world would you like for this campaign?",
            choices=[
                "🆕 Create a brand new world for this campaign",
                "🏛️ Use an existing world (coming soon)",
                "🎲 We will craft a world for you (auto-generate)",
                "❌ Cancel campaign creation"
            ]
        ).execute()
        
        if "❌ Cancel" in world_choice:
            return False
        elif "🏛️ Use an existing" in world_choice:
            print("🚧 Existing world selection coming soon!")
            print("📝 For now, you can add a world later from the World Builder menu.")
            return True
        elif "🎲 We will craft" in world_choice:
            result = self.orchestrate_world_generation(campaign_id, self.get_auto_parameters(campaign_name))
            return result.success
        elif "🆕 Create a brand new" in world_choice:
            result = self.orchestrate_world_generation(campaign_id, self.get_user_world_parameters())
            return result.success
            
        return True


        # PARAMETER SOURCES
    def get_user_world_parameters(self) -> Dict[str, Any]:
        """Get parameters from user via CLI"""
        world_builder_cli = WorldBuilderCLI()
        return world_builder_cli.get_world_parameters()
    

    def get_auto_parameters(self, campaign_name: str) -> Dict[str, Any]:
        """Get predefined auto-generation parameters"""
        auto_params = {
            'theme': 'High Fantasy - Magic is everywhere, heroes are legendary',
            'magic_commonality': 'Common - Most towns have a wizard or healer',
            'deity_structure': 'Pantheon - Multiple gods with distinct domains',
            'major_threat': 'Ancient Evil - Something terrible stirs from long slumber',
            'size': 'Regional - Small continent (3 kingdoms, 3-5 major cities, 15-20 settlements)',
            'custom_details': f'Classic fantasy adventure setting for the {campaign_name} campaign'
        }
        return auto_params

    def orchestrate_world_generation(self, campaign_id: str, parameters: Dict[str, Any]) -> WorldGenerationResult:
        """Generate a complete world through sequential bot phases"""
        try:
            print("🌍 Starting world generation phases...")
            
            # Phase 1: Universe Foundation (IMPLEMENTED)
            print("🌌 Phase 1: Generating universe foundation...")
            universe_data = self.universe_builder.generate_universe_context(parameters)
            world_name = universe_data.get('world_info', {}).get('world_name', 'Generated World')
            
            # Phase 3: Database Storage
            print("💾 Phase 3: Creating world record and processing world content...")
            world_id = create_world_record(campaign_id, universe_data)
            ContentProcessorAgent(debug=True).process_universe_content_batch(campaign_id=campaign_id, universe_data=universe_data, world_id=world_id)

            # Phase 2: Regional Development NOT ANYTHING YET
            print("🗺️ Phase 2: Regional development...")
            regions = self.regional_builder.generate_regions_for_world(universe_data)
            
            
            # Phase 4: Settlement Networks (PLACEHOLDER)
            print("🏘️ Phase 4: Settlement networks... (coming soon)")
            settlements = []  # TODO: Call settlement_builder when implemented
            
            # Phase 5: NPC Networks (PLACEHOLDER)
            print("👥 Phase 5: NPC networks... (coming soon)")
            npcs = []  # TODO: Call npc_builder when implemented
            
            # Phase 6: Conflict Webs (PLACEHOLDER)
            print("⚔️ Phase 6: Conflict webs... (coming soon)")
            conflicts = []  # TODO: Call conflict_builder when implemented
            
            # Phase 7: Quest Networks (PLACEHOLDER)
            print("📜 Phase 7: Quest networks... (coming soon)")
            quests = []  # TODO: Call quest_builder when implemented
                
            print("✅ Universe foundation complete! (Further phases in development)")

            
            return WorldGenerationResult(
                success=True,
                world_name=world_name,
                world_data=universe_data,
                regions=regions,
                settlements=settlements,
                npcs=npcs,
                conflicts=conflicts,
                quests=quests
            )
            
        except Exception as e:
            print(f"❌ World generation failed: {str(e)}")
            return WorldGenerationResult(success=False, error=str(e))

    def handle_region_planning_for_campaign(self, campaign_id: str, campaign_name: str, world_id: str, universe_data: Dict[str, Any]) -> bool:
        """Delegate region planning to the regional builder"""
        return self.regional_builder.handle_region_planning_for_campaign(campaign_id, campaign_name, world_id, universe_data)

def main():
    """Main function for standalone world builder execution"""
    print("🌍 Agentic World Builder - Standalone Test")
    print("=" * 50)
    
    orchestrator = WorldGenerationOrchestrator()
    
    # Test with auto parameters
    result = orchestrator.orchestrate_world_generation("test_campaign", orchestrator.get_auto_parameters("Test Campaign"))
    
    if result.success:
        print(f"✅ Success! Generated world: {result.world_name}")
    else:
        print(f"❌ Failed: {result.error}")

if __name__ == "__main__":
    main()