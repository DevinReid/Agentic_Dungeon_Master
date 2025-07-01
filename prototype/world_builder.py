# world_builder.py
"""
World Builder Orchestrator
Main script for coordinating world generation across multiple AI bots
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
from bots.world_builder.universe_builder import UniverseBuilder
from bots.world_builder.regional_builder import RegionalBuilder  
from bots.world_builder.settlement_builder import SettlementBuilder
from bots.world_builder.npc_network_builder import NPCNetworkBuilder
from bots.world_builder.conflict_builder import ConflictBuilder
from bots.world_builder.quest_network_builder import QuestNetworkBuilder

@dataclass
class WorldGenerationResult:
    success: bool
    world_name: str = ""
    regions: List[Dict] = None
    settlements: List[Dict] = None 
    npcs: List[Dict] = None
    conflicts: List[Dict] = None
    quests: List[Dict] = None
    error: str = ""

class WorldGenerationOrchestrator:
    """Main orchestrator for world generation process"""
    
    def __init__(self):
        self.universe_builder = UniverseBuilder()
        self.regional_builder = RegionalBuilder()
        self.settlement_builder = SettlementBuilder()
        self.npc_builder = NPCNetworkBuilder()
        self.conflict_builder = ConflictBuilder()
        self.quest_builder = QuestNetworkBuilder()

    def generate_complete_world(self, campaign_id: str, parameters: Dict[str, Any]) -> WorldGenerationResult:
        """Generate a complete world with all layers"""
        try:
            print("🌍 Starting complete world generation...")
            
            # Layer 1: Cosmic/Universe Level
            print("🌌 Generating universe foundation...")
            universe = self.universe_builder.generate_campaign_universe(campaign_id, parameters.get('theme', 'fantasy'))
            
            # Layer 2: Regional Level  
            print("🗺️ Generating regions...")
            regions = []
            region_count = self._get_region_count(parameters.get('size', 'Medium'))
            for i in range(region_count):
                region = self.regional_builder.generate_region(universe, f"region_{i}")
                regions.append(region)
            
            # Layer 3: Settlement Level
            print("🏘️ Generating settlements...")
            settlements = []
            for region in regions:
                settlement_count = self._get_settlement_count_per_region(parameters.get('size', 'Medium'))
                for j in range(settlement_count):
                    settlement = self.settlement_builder.generate_settlement(region, f"settlement_{j}")
                    settlements.append(settlement)
            
            # Layer 4: NPC Network
            print("👥 Generating NPC networks...")
            all_npcs = []
            for settlement in settlements:
                npcs = self.npc_builder.generate_settlement_npcs(settlement)
                all_npcs.extend(npcs)
            
            # Layer 5: Conflict Web
            print("⚔️ Generating conflicts...")
            conflicts = self.conflict_builder.generate_conflict_layers({
                'universe': universe,
                'regions': regions, 
                'settlements': settlements,
                'npcs': all_npcs
            })
            
            # Layer 6: Quest Network
            print("📜 Generating quest networks...")
            quests = self.quest_builder.generate_interconnected_quests(conflicts, all_npcs, settlements)
            
            # Save to database
            print("💾 Saving to database...")
            self._save_world_to_database(campaign_id, universe, regions, settlements, all_npcs, conflicts, quests)
            
            print("✅ World generation complete!")
            
            return WorldGenerationResult(
                success=True,
                world_name=universe.get('world_info', {}).get('world_name', 'Generated World'),
                regions=regions,
                settlements=settlements,
                npcs=all_npcs,
                conflicts=conflicts,
                quests=quests
            )
            
        except Exception as e:
            print(f"❌ World generation failed: {str(e)}")
            return WorldGenerationResult(success=False, error=str(e))

    def generate_test_settlement(self, campaign_id: str, settlement_name: str = "Oakwood Village") -> WorldGenerationResult:
        """Generate a single test settlement for development/testing"""
        try:
            print(f"🏰 Generating test settlement: {settlement_name}")
            
            # Create minimal context for test
            test_universe = {"cosmic_setting": {"world_name": "Test World", "theme": "fantasy"}}
            test_region = {"region_name": "Test Region", "geography": {"terrain": "forested hills"}}
            
            # Generate settlement
            settlement = self.settlement_builder.generate_settlement(test_region, settlement_name)
            
            # Generate NPCs for settlement
            npcs = self.npc_builder.generate_settlement_npcs(settlement)
            
            # Generate simple local conflicts
            conflicts = self.conflict_builder.generate_local_conflicts(settlement, npcs)
            
            # Save test data
            self._save_test_settlement(campaign_id, settlement, npcs, conflicts)
            
            print("✅ Test settlement generated!")
            
            return WorldGenerationResult(
                success=True,
                world_name="Test World",
                settlements=[settlement],
                npcs=npcs,
                conflicts=conflicts
            )
            
        except Exception as e:
            print(f"❌ Test settlement generation failed: {str(e)}")
            return WorldGenerationResult(success=False, error=str(e))

    def _get_region_count(self, size: str) -> int:
        """Get number of regions based on size parameter"""
        size_map = {
            "Small": 1,
            "Medium": 3, 
            "Large": 5
        }
        return size_map.get(size.split()[0], 3)

    def _get_settlement_count_per_region(self, size: str) -> int:
        """Get number of settlements per region"""
        size_map = {
            "Small": 3,
            "Medium": 3,
            "Large": 4
        }
        return size_map.get(size.split()[0], 3)

    def _save_world_to_database(self, campaign_id, universe, regions, settlements, npcs, conflicts, quests):
        """Save complete world data to database"""
        # TODO: Implement database storage
        print("🚧 Database storage not yet implemented")
        pass

    def _save_test_settlement(self, campaign_id, settlement, npcs, conflicts):
        """Save test settlement data"""
        # TODO: Implement test data storage
        print("🚧 Test data storage not yet implemented")
        pass

def main():
    """Main function for standalone world builder execution"""
    print("🌍 Agentic World Builder")
    print("========================")
    
    orchestrator = WorldGenerationOrchestrator()
    
    # Example usage
    test_params = {
        "theme": "High Fantasy",
        "size": "Small (1 region, 3 settlements)",
        "magic_level": "High"
    }
    
    result = orchestrator.generate_test_settlement("test_campaign", "Oakwood Village")
    
    if result.success:
        print(f"✅ Success! Generated world: {result.world_name}")
    else:
        print(f"❌ Failed: {result.error}")

if __name__ == "__main__":
    main()