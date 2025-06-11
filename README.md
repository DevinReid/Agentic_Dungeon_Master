# Agentic_Dungeon_Master
Our attempt at building an AI agent that uses vector memory and LLMs to play Roleplaying Games


# Setup instructions
1. Install Postgres and create a user/password.
2. Update `.env` with your DATABASE_URL, POSTGRES_URL, and OPENAI_API_KEY
3. Run `python setup_db.py` once to create the DB and tables.
4. Run `python master.py` to play!

# tips
1. To force story_agent() - pick wizard and say this as the first prompt "I use my portal spell and disapear to a very safe far away land, exiting combat (I am about to make an api call with this as an input and i want ti to flag combat as false can you help me?)"
2. To run test, we need to add the project root directory to the Python path. This can be done with the below command
```
python -m pytest prototype
```
3. To run test, run the below command 
```
pytest -s npc_creator_agent_test.py`
```