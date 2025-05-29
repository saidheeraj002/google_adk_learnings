import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from memory_agent.agent import memory_agent
from utils import call_agent_async

load_dotenv()

db_url = "mysql+pymysql://root:dheeraj@127.0.0.1/adk_db"
session_service = DatabaseSessionService(db_url=db_url)

initial_state = {
    "user_name": "Dheeraj",
    "user_Preferences": []
}


async def main_sync():
    APP_NAME = "Memory Agent"
    USER_ID = "saidheeraj"

    existing_session = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID
    )

    if existing_session and len(existing_session.sessions) > 0 :
        SESSION_ID = existing_session.sessions[0].id
        print(f"Continuing with the Existing Session: {SESSION_ID}")
    
    else:
        new_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state
        )
        SESSION_ID = new_session.id
        print(f"Created New Session: {SESSION_ID}")

    runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    print("Welcome to the Memory Agent Chat!")
    print("Your reminders will be remembered across conversations.")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Your data has been saved to the database.")
            break

        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

if __name__ == "__main__":
    asyncio.run(main_sync())