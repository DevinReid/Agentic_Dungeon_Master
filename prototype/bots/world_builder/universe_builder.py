import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import typer
from typing import Dict, Any, Optional, List

# Load environment variables
load_dotenv()

class UniverseBuilder:
    """
    AI-powered universe generation for D&D worlds.
    Handles cosmic-level worldbuilding: themes, magic systems, pantheons, global threats.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize with OpenAI client"""
        self.debug = True  # TODO: Make configurable
        
        try:
            if openai_api_key:
                self.client = OpenAI(api_key=openai_api_key)
            else:
                # Will use OPENAI_API_KEY environment variable
                self.client = OpenAI()
        except Exception as e:
            self.client = None
            if self.debug:
                typer.secho(f"⚠️ OpenAI client initialization failed: {e}", fg=typer.colors.YELLOW)
        
    def generate_universe_context(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete universe context from world builder parameters.
        Args:
            parameters: Dict containing all user choices (theme, size, magic_commonality, etc.)
        
        Returns:
            Dict containing complete universe context for other builders
        """
        if self.debug:
            typer.secho(f"🌌 UniverseBuilder: Generating universe context...", fg=typer.colors.CYAN)
            typer.secho(f"   Parameters: {parameters}", fg=typer.colors.YELLOW)
        
        # Generate universe using AI with all parameters as context
        universe_context = self._generate_with_ai(parameters)
        
        if self.debug:
            world_name = universe_context.get('world_info', {}).get('world_name', 'Unknown')
            typer.secho(f"✅ Universe context generated: {world_name}", fg=typer.colors.GREEN)
            typer.secho(f"   Size: {universe_context['size']['scope']} ({universe_context['size']['region_count']} regions, {universe_context['size']['major_city_count']} cities, {universe_context['size']['settlement_count']} settlements)", fg=typer.colors.BLUE)
        
        return universe_context
    
    def _generate_with_ai(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI to generate universe context"""
        
        # Check if client is available
        if not self.client:
            if self.debug:
                typer.secho("❌ OpenAI client not available", fg=typer.colors.RED)
            raise Exception("OpenAI client not initialized - check API key")
        
        # Build the prompt
        prompt = self._build_universe_prompt(parameters)
        
        if self.debug:
            typer.secho("🤖 Calling OpenAI for universe generation...", fg=typer.colors.BLUE)
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON response
        try:
            ai_result = json.loads(content)
            return ai_result
        except json.JSONDecodeError as e:
            if self.debug:
                typer.secho(f"⚠️ AI returned invalid JSON: {content}", fg=typer.colors.YELLOW)
            raise Exception(f"AI returned malformed JSON: {e}")
    
    def _build_universe_prompt(self, parameters: Dict[str, Any]) -> str:
        """Build the prompt for AI universe generation"""
        
        prompt = f"""Create a D&D universe based on these user choices:

{json.dumps(parameters, indent=2)}

INSTRUCTIONS:
- When you see choices like "🎲 Decide for me: [text]", generate that element completely from scratch using the hint text as inspiration
- When you see specific choices like "Regional - Small continent...", use that as creative inspiration but expand it into rich, atmospheric descriptions
- All output should be evocative and flavorful - transform simple choices into vivid world-building details
- Don't copy user text literally - use it as creative fuel for beautiful, immersive descriptions
- If world_name is provided and not empty, use that exact name; if empty or missing, generate an evocative world name

Return a JSON object with this structure:
{{
    "world_info": {{
        "world_name": "evocative world name",
        "world_description": "comprehensive overview of the world and its cosmic history",
        "theme_description": "detailed description of the world's overall narrative theme",
        "theme_list": "comma-separated list of core narrative elements",
        "natural_laws": "unique physics, planar connections, or special world rules",
        "custom_details": "integration of any user-provided custom details into world context"
    }},
    "magic_system": {{
        "commonality": "rich description of magic prevalence",
        "mechanics": "how magic works in this world",
        "limitations": "what restricts magical power",
        "sources": "where magic comes from",
        "magic_level": "Extremely High/High/Medium/Low/Extremely Low - based on overall world context"
    }},
    "pantheon": {{
        "structure": "description of religious organization", 
        "major_deities": ["list of important gods"],
        "religious_conflicts": ["tensions between faiths"],
        "divine_influence": "how active gods are"
    }},
    "global_threats": [
        {{
            "primary_threat": "main world-spanning danger",
            "threat_details": "specific antagonists and timeline",
            "world_impact": "how threat affects daily life",
            "resistance_forces": "who opposes the threat"
        }}
    ],
    "size": {{
        "scope": "intimate/regional/continental/wilderness",
        "description": "narrative description of world scale",
        "region_count": number_of_major_regions,
        "major_city_count": number_of_major_cities_across_world,
        "settlement_count": number_of_smaller_towns_villages_across_world
    }}
}}

For the size field, use these guidelines:
- intimate: 1-2 regions, 1-3 cities, 5-15 settlements
- regional: 3-5 regions, 3-8 cities, 15-40 settlements  
- continental: 6-10 regions, 8-20 cities, 40-100 settlements
- wilderness: 2-4 regions, 0-1 cities, 0-5 settlements

WILDERNESS SCOPE: For untamed/undeveloped lands (new continents, unexplored regions):
- Emphasize natural geography over political boundaries
- Focus on landmarks, ruins, natural hazards rather than towns
- Settlements should be camps, outposts, or small indigenous communities
- Regions defined by terrain/climate, not kingdoms or nations

GLOBAL THREATS HANDLING:
- The global_threats field is a LIST of threats (user may have selected multiple)
- Create one threat object for each threat in the user's global_threats list
- If user selected "None Yet", create an empty list []
- Keep each threat focused with just: primary_threat, threat_details, world_impact, resistance_forces
- Make threats feel interconnected where logical but each should be distinct
- Vary the scale, timeline, and focus of each threat for compelling variety

MAGIC LEVEL GUIDELINES:
- magic_level should reflect the OVERALL magical presence in the world, considering all context
- Extremely High: Magic is fundamental to reality, reshapes physics, everyone uses it daily
- High: Magic is common, most people interact with it, shapes society significantly  
- Medium: Magic exists but is special, known but not universal, moderate impact
- Low: Magic is rare, whispered about, minimal impact on daily life
- Extremely Low: Magic barely exists or doesn't exist at all, purely mundane world
- Consider custom details heavily - if user wants "no magic, just steel and blood" = Extremely Low
- Consider all contradictions - "no magic but everyone is a seahorse" = Extremely Low (magic) but fantastic (species)

Make everything cohesive and interconnected across the entire universe."""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI universe generation"""
        return """You are an expert D&D worldbuilder and narrative designer. You create rich, interconnected fantasy universes that feel lived-in and authentic.

Your role is to transform player choices into vivid, atmospheric world descriptions:
- When given player inspiration (like "Common - Most towns have a wizard"), expand it into rich, evocative descriptions that capture the essence while adding depth and atmosphere
- Don't copy player text literally - use it as creative fuel for beautiful, immersive descriptions
- All content should feel like it belongs in a fantasy novel - atmospheric, detailed, and engaging
- Make everything feel connected and purposeful across the universe
- Create compelling conflicts and tensions at every level
- Ensure magic systems have clear rules and limitations that feel organic to the world
- Make religions feel like real belief systems with real conflicts and cultural impact
- Ground threats in believable motivations and capabilities that affect daily life
- Always return valid JSON in the exact format requested
- Be creative but internally consistent across all elements"""
    

    



