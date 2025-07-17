#!/usr/bin/env python3
"""
Generate sample universe JSON outputs for database design analysis
"""

import json
import sys
import os
from datetime import datetime

# Add the prototype directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bots.world_builder.universe_builder import UniverseBuilder
import re

# Test parameters from your existing test file
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

def format_as_markdown(obj, title="Universe Data", level=1):
    """Convert JSON object to readable Markdown format"""
    md_lines = []
    
    if level == 1:
        md_lines.append(f"# {title}\n")
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            header_level = "#" * (level + 1)
            md_lines.append(f"{header_level} {key.replace('_', ' ').title()}\n")
            
            if isinstance(value, (dict, list)):
                md_lines.append(format_as_markdown(value, level=level + 1))
            else:
                # Format strings with proper line breaks
                if isinstance(value, str):
                    # Split at sentence boundaries for readability
                    sentences = re.split(r'(?<=[.!?])\s+', str(value))
                    if len(sentences) > 1:
                        formatted_text = '\n\n'.join(sentences)
                    else:
                        formatted_text = str(value)
                    md_lines.append(f"{formatted_text}\n")
                else:
                    md_lines.append(f"{value}\n")
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                md_lines.append(f"### Item {i + 1}\n")
                md_lines.append(format_as_markdown(item, level=level + 1))
            else:
                md_lines.append(f"- {item}\n")
    
    return '\n'.join(md_lines)

def generate_and_save_universe(parameters, filename_prefix):
    """Generate universe and save to JSON file"""
    print(f"🌌 Generating universe: {filename_prefix}")
    
    try:
        builder = UniverseBuilder()
        result = builder.generate_universe_context(parameters)
        
        # Create filenames with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"{filename_prefix}_{timestamp}.json"
        md_filename = f"{filename_prefix}_{timestamp}.md"
        
        # Save JSON file (for data structure analysis)
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, separators=(',', ': '))
        
        # Save Markdown file (for human readability)
        world_name = result.get('world_info', {}).get('world_name', filename_prefix)
        markdown_content = format_as_markdown(result, f"Universe: {world_name}")
        
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Saved files:")
        print(f"   📄 JSON: {json_filename}")
        print(f"   📖 Markdown: {md_filename}")
        print(f"   World: {result.get('world_info', {}).get('world_name', 'Unknown')}")
        print(f"   Size: {result.get('size', {}).get('scope', 'Unknown')} ({result.get('size', {}).get('region_count', 0)} regions)")
        
        return json_filename, result
        
    except Exception as e:
        print(f"❌ Failed to generate {filename_prefix}: {e}")
        return None, None

def main():
    """Generate sample universes for database design analysis"""
    print("🚀 Generating Universe Builder sample outputs...")
    print("   These will be used for database schema design\n")
    
    # Generate basic fantasy world
    basic_file, basic_result = generate_and_save_universe(basic_parameters, "universe_basic_fantasy")
    
    print()
    
    # Generate weird cat world
    cat_file, cat_result = generate_and_save_universe(cat_parameters, "universe_cat_space")
    
    print("\n📋 Files Generated:")
    if basic_file:
        basic_md = basic_file.replace('.json', '.md')
        print(f"   📄 Basic Fantasy JSON: {basic_file}")
        print(f"   📖 Basic Fantasy Markdown: {basic_md}")
    if cat_file:
        cat_md = cat_file.replace('.json', '.md')
        print(f"   📄 Cat Space JSON: {cat_file}")
        print(f"   📖 Cat Space Markdown: {cat_md}")
    
    print("\n🎯 Next Steps:")
    print("   1. Review the Markdown files for readability")
    print("   2. Review the JSON structure for database design")
    print("   3. Create ArtifactExtractor patterns")
    print("   4. Plan vectorization chunking strategy")

if __name__ == "__main__":
    main() 