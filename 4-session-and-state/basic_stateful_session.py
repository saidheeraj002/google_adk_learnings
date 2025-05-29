import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from question_answering_agent.agent import question_answering_agent
import asyncio

load_dotenv()

async def call_agent_async(runner, user_id, session_id, query):

    new_message = types.Content(role="user", parts=[types.Part(text=query)])
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Final Response: {event.content.parts[0].text}")

    print("==== Session Event Exploration ====")
    session = runner.session_service.get_session(
        app_name=runner.app_name, user_id=user_id, session_id=session_id
    )

    print("state_items", session.state.items())

    # Log final Session state
    print("=== Final Session State ===")
    for key, value in session.state.items():
        print(f"{key}: {value}")


async def stateful_session_example():

    session_service_stateful = InMemorySessionService()

    initial_state = {
        "user_name": "",
        "user_preferences": []
    }

    # Create a NEW session
    APP_NAME = "Sai"
    USER_ID = "dheeru"
    SESSION_ID = str(uuid.uuid4())

    stateful_session = session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )

    print("CREATED NEW SESSION:")
    print(f"\tSession ID: {SESSION_ID}")

    runner = Runner(
        agent=question_answering_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )
    
    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Your data has been saved to the database.")
            break

        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)


if __name__ == "__main__":
    asyncio.run(stateful_session_example())