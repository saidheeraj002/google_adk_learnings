import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
# from .book_my_show_agent.agent import book_my_show_agent
from utils import add_user_query_to_history, call_agent_async
from book_my_show_agent.agent import book_my_show_agent
load_dotenv()

session_service = InMemorySessionService()

initial_state = {
    "user_name": "Sai Dheeraj",
    "movies_info_list": [],
    "interaction_history": [],
    "tickets_booked": []
}


async def main_async():
    APP_NAME = "Book My Show"
    USER_ID = "#1234"

    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )

    SESSION_ID = new_session.id
    print(f"Created new session: {SESSION_ID}")

    runner = Runner(
        agent=book_my_show_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("\nWelcome to Book My Show Services!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break

        await add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, user_input
        )

        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    final_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("\nFinal Session State:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")


def main():
    """Entry point for the application."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()