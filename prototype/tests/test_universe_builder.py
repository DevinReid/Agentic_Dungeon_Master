#!/usr/bin/env python3

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bots.world_builder.universe_builder import UniverseBuilder

basic_parameters = {
    'theme': 'High Fantasy - Magic is everywhere, heroes are legendary',
    'magic_commonality': 'Common - Most towns have a wizard or healer',
    'deity_structure': 'Pantheon - Multiple gods with distinct domains',
    'major_threat': 'Ancient Evil - Something terrible stirs from long slumber',
    'size': 'Regional - Small continent (3 kingdoms, 3-5 major cities, 15-20 settlements)',
    'custom_details': 'Classic fantasy adventure setting'
}

cat_parameters = {
    'theme': 'weird space fantasy, low tech',
    'magic_commonality': 'Magic cant exist here',
    'deity_structure': 'No gods, just cat worship',
    'major_threat': 'There is a door that is closed, and it is not a good thing for the cats',
    'size': 'it is an island in space',
    'custom_details': 'cat worshiping space society'
}

def test_basic_parameters():
    builder = UniverseBuilder()
    result = builder.generate_universe_context(basic_parameters)
    universe_builder_outputs(result)
    print(result)

def test_cat_parameters():

    builder = UniverseBuilder()
    result = builder.generate_universe_context(cat_parameters)
    universe_builder_outputs(result)
    print(result)


def universe_builder_outputs(result):

    
    # Test all world_info fields are not empty
    world_info = result['world_info']
    assert world_info['world_name'] != ""
    assert world_info['world_description'] != ""
    assert world_info['theme_description'] != ""
    assert world_info['theme_list'] != ""
    assert world_info['natural_laws'] != ""
    assert world_info['custom_details'] != ""
    
    # Test all size fields
    size = result['size']
    assert size['scope'] != ""
    assert size['description'] != ""
    assert isinstance(size['region_count'], int)
    assert isinstance(size['major_city_count'], int)
    assert isinstance(size['settlement_count'], int)
    
    # Test all magic_system fields
    magic = result['magic_system']
    assert magic['commonality'] != ""
    assert magic['mechanics'] != ""
    assert magic['limitations'] != ""
    assert magic['sources'] != ""
    assert magic['magic_level'] in ['Extremely High', 'High', 'Medium', 'Low', 'Extremely Low']
    
    # Test all pantheon fields
    pantheon = result['pantheon']
    assert pantheon['structure'] != ""
    assert isinstance(pantheon['major_deities'], list)
    assert isinstance(pantheon['major_deities'], list)
    assert pantheon['divine_influence'] != ""
    
    # Test global_threats
    threats = result['global_threats']
    assert len(threats) > 0
    for threat in threats:
        assert threat['primary_threat'] != ""
        assert threat['threat_details'] != ""
        assert threat['world_impact'] != ""
        assert threat['resistance_forces'] != ""

        