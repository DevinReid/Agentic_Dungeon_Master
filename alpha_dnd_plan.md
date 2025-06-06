6/5/25
From Kyle McVeigh
To Devin Reid

# Overview 
This document serves as a proposed Alpha Plan for building a DnD Game powered by AI 

## Goals 
* Goal to test the AI's ability to successfully use Vector stores to create more realistic Dungeon Master Skills 
* Test the 'fun' of choices 
* Test the use of summaries to create artifacts (Campaign summaries, Session summaries, character story lines, character motivation, item descriptions, place descriptions, etc.)
* Test use of Python SqlModel to be helpful 
* Get feedback from DnD users on what we missed, if it feels fun, what information they would need to see, how many choices to give them, how much structure to give them, etc etc 
* Create Summary Bot, DM Bot, and Combat Bot and test its effectiveness through unit tests 

## Technology Choices
* Python Language
* SqlModel ORM
* Database Postgres 
* Interface, CLI tool using [Typer](https://typer.tiangolo.com/)
* OpenAI Intergrations with [Vector store](https://platform.openai.com/docs/guides/retrieval#vector-stores)

## Expected Game plan
1. User clones the repo and runs initial set up in the terminal
2. User interacts with the game via the terminal
3. User can start a new campaign and have some input on the set up 
4. User starts a session, interacts with DM 
5. User can engage in combat 
6. User can look at their artifacts (character sheet, inventory, etc)
7. User can send a session 
9. User can level up
9. User can go to an existing campaign and have all features saved 

## Required Body of work 
This an ordered body of work that serves more as a guide rather than a checklist. More work will be required, do not expect this to be a complete list. 
0. Make an enity relationship diagram for the required sql tables to review before implementation
1. Create the initial repo and Typer hello world interface 
2. Tool has a flow to add a open ai token and create a local postgres database. If this exist skip this step.
3. Create related migrations for campaigns, characters, and inventory
4. Tool pulls in existing campaigns from the local database  xxfor selection or allows for creation of new campaigns 
5. Creates of an initial AI DM Agent 
6. New Campaign creates the initial entries in the database and using the AI DM 
7. Artifacts are automatically created an updated using a summary AI Agent
8. User can interact with AI DM and artifacts are saved and updated 
9. AI DM reviews artifacts during interaction 
10. User can see the artifacts (story recap, character recap, inventories, campaign recap)
11. Combat can happen powered by a separate AI agent 
12. A session can end and save down 
13. A campaign can be loaded and the previous session is remembered 

## Expected Timeline
The alpha plan is a fairly long project. If the Alpha goes well and we get everything humming the beta will take shorter to launch than the alpha and be way less risk. I think the Alpha will seriously take at least 3 months and at most of 9. 

## Further steps 
If we build this and get good feedback, the next steps would be to build a true web based frontend and set up a shared hosted database. Additionally we'll need to turn the typer functions into API endpoints

## Other notes 
* Devin, you should be able to do most of the development work. That was the big inspiration of mine to do this as a CLI tool in Python. I think this is a good test of your skills that you can pass with guidance 
* There is a world where if this is really good we can sell it. There are tons of CLI tools that cost money. It could ideally feel like a really good 80s text based video game. A stretch goal would be to demo it at dragon con or local dragon cons and try to raise money.
* I'd love to use [Beekeeper Studio](https://www.beekeeperstudio.io/) as a developer debugging tool for what is in the database locally. Just to keep that in mind. 