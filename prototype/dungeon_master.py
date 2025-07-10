# dungeon_master.py
from services.start_menu import start_menu





def main():
    """Main entry point"""
    print("Welcome to the Agentic D&D Dungeon Master!")

    
    try:
        start_menu()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your database connection and try again.")

if __name__ == "__main__":
    main()
