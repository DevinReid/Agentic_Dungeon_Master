TODO:
- Test All of the processing bots, push them to limits
- Build better entity structure, update tables to reflect this (ie add items table, make artifcats an item type rather than its own table, make dieties a type of npc ect)
- refactor this ugly ass code base( mostly the dungeon_matster, this should be like 50 lines just like running modules)
- Build a dual model test to see how often 4o mini fails at pulling specific numbers into outputs, also test quality 

## Worldbuilder thoughts and architecture ideas 6/28
Okay so I want to build this to be a way to explore building agentic AI from scratch
currently, I want to build a story agent that build a complete if not world, then at least a starting quest, some npcs a bad guy, and some quests
this information should be done by openAI bots making prompts for OpenAI prompts leading down to python functions
Ideally we create a universe, and also use AI to scan each part of the universe for relevant data, storing that in our database

so we are basically testing saving data down, and then using that data as context for new narrations and stories by the dm and player

Ideally, I can also utilize some kind of vector database to rapidly grab relational information, if that is even neccesary

the current app needs alot of tweaking and alot more ai bots but I want to maybe start with creating a small test world or test parameters, and buil;d from there.


lets maybe talk more broad about a structure for the worldbuilder, I want this to build and store alot of different kinds of information that could come up in the game.
lets come up with what we might create at the beggining of a session to get really detailed, 

- So im thinking well need a larger world setting, this could be the entire planet, continetnt or just a kingdom, this world might even exist at the campaign Level? like you could run multiple chracters in different settings in the same universe? I guess thats kind of how we have this set up now. this sould probably contain top level information about the world, geo politics, landscapes, ect
- Well probably want to generate a more local setting, something the players will actually spend most of their time in, so maybe a state or territory sized thing, or even maybe after creating the Larger World setting, This could break that down into smaller reegions, maybe then bnroken down into a list of  towns, geographical imprtances, and then maybe we copuld have  an entire other bot generate details for that town, then also maybe generate some dungeons for the map for players to find and explore whetehr thaey be in towns or the wilderness
- We would want to take those towns and break them down into builings, cultural ideas, items of Note, and of course
- Generate all of the NPCs (or relevant ones or most of them). This would include things like, what they did in town / for the town, who they were related to, any notable positive or negative relationships, where they live in town, personality traits that might help build flavor (quirks, flaws, achievments, ect), then generate character sheets for each. We might also generate an inventory for each so thiose things are set at first, perhaps making later ai bots and analyzers 
- We would then   probably want to generate some kind of conflict, maybe on different levels, maybe city to city / kingdom to kingdom / planet v civilization, a high level almost setting kind of plot conflict, then wed want to build some antagonists for the players to know about, work towards, maybe chosing a big bad, or leaving that for a lower tier of plot.  I guess then youd want to make more local history and conflict for the players to realy engage with, with maybe starting to introduce thenidea of quests
- creating quests, ideally these are not strict ending quests, but maybe for the sake of testing they should be? in balders gate 3 the quest design is very much on a conflict level, not a hard coded like "Kill 5 gnolls and return to the farmer" To complete the quest you must resolve the conflict, so you could befriend the gnolls, sside with them and kill the farmer, maybe help them raid the town, or even borkere p[eace bewteeen the two parties, or simply kill the gnolls or maybe kill everyone, in any of those casses the conflict would be resolved and perhaps exp would be rewarded based on some system of how difficult or maybe just impactful the solve was, not sure on this
- Only other thing i could think of is expanding on like economies, histories, lore ect. all of this to feed into the robot to make consistent decisions.
- If im missing any other ideas, please tell em what you think
- the entire purpose of all oif this information should be to be broken down and parsed into a json format to be stored as artifacts of story data in our postgresql database, to be fed back into the ai narrator somehow so things stay on track.   The feeding back in might be where my vector data comes into play, im not sure about how that works really, but id love to learn, but maybe we need to grab all of the data first? or maybe the vector relationships need to be built in from the begining to be effective?


[1] Save to world_content (full essays)
    ↓  
[2] ArtifactExtractor → extracted_entities (NPCs, places, etc.)
    ↓
[3] VectorizeBot → content_embeddings (searchable snippets)  

## Vector save and feed worklow

1. Player creates world → UniverseBuilder generates JSON
2. JSON saved to PostgreSQL (worlds + world_content tables)  
3. Content automatically embedded via OpenAI → stored in Pinecone
4. to feed: AI agents query: "Do I need any context for {user input} or {narration summary}" 
5. Pinecone finds semantically similar content that was saved as vector embeddings. 
6. PostgreSQL provides full details on the query
7. second AI narrator gets perfect context for responses, the results from #6's query

timeline patterns??? 

build 

entities = self._ai_extract_entities(content, ...)
resolved_entities = self._ai_resolve_and_individuate(entities, context_data)

## NPC Tier System 7/2/2025

**Tier 1 NPCs: Full Database Records (PostgreSQL)**
- Complete stat blocks, personality, wants/needs, quest hooks, secrets
- Generated when: Player directly interacts (conversation, combat)
- Storage: Full PostgreSQL npc table with all gameplay mechanics

**Tier 2 NPCs: Roleplay Profiles (Vector DB)**  
- Name, personality, simple want, notable trait, relationships
- Generated when: NPC mentioned/asked about but not directly encountered
- Storage: Rich vector chunks with personality and roleplay info

**Tier 3 NPCs: Names + Context (Simple Vectors)**
- Just name and basic context ("Thomas the Baker - runs morning bread route")
- Generated during: Settlement creation for population atmosphere
- Storage: Lightweight vector chunks, easily promotable

**Promotion Flow:**
Settlement Builder → Tier 3 population → Tier 2 (if mentioned) → Tier 1 (if interacted)

**Storage Strategy:**
- Tier 1: PostgreSQL (structured gameplay data)
- Tier 2: Vector DB (rich personality descriptions) 
- Tier 3: Simple vectors (name + minimal context)
- All tiers searchable via vector queries for natural language access


Content → contentProcessor
↓       ↓
↓ ------→TagGenerator ────────→ ContentProcessor (orchestrator)
↓       ↓               ↓
↓------→→-------------- → EntityExtractor (raw 5-field) → ContentProcessor 
↓       ↓                               ↓   ↓
↓       →------------------------------→↓   ↓-------→ EntityProcessor (heavy records) ────→ Direct to Database (bypass ContentProcessor)
↓       ↓                               ↓                                            ↓
↓       ↓                               ↓                                            ------→VECTORIZER
↓       ↓                               ↓
→------→↓-------------------------------→--------→ ContentChunker ──────────→ ContentProcessor
                                                                ↓
                                                                --------→VECTORIZER

        contentProcessor -> Save to Postgres db

