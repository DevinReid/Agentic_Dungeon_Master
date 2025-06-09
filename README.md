# Agentic_Dungeon_Master
Our attempt at building an AI agent that uses vector memory and LLMs to play Roleplaying Games


# Setup instructions
1. Install Postgres and create a user/password.
2. Update `.env` with your DATABASE_URL, POSTGRES_URL, and OPENAI_API_KEY
3. Run `python setup_db.py` once to create the DB and tables.
4. Run `python cli.py` to play!
