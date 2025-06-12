from dotenv import load_dotenv
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai.types import Content, Part
from smart_memory_agent.agent import agent

PINECONE_API_KEY="pcsk_4gQsLN_PDNbGoZbjStT8sqdPSCyrTJMvz6rnULgJyJzbmQrMhCnVtHj34apJK4B7xPSgpC"

load_dotenv()

APP_NAME = "smart_memory_agent"
USER_ID = "cli_user"

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

SLIDING_WINDOW_SIZE = 5
MEMORY_RETRIEVAL_TOP_K = 3

async def main():
    print("Welcome to the Smart Memory CLI! Type 'exit' to quit.")
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    conversation_history = []

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # 1. Add user input to history
        conversation_history.append(f"User: {user_input}")

        # 2. Retrieve relevant memories from long-term memory
        memory_results = await memory_service.search_memory(
            app_name=APP_NAME,
            user_id=USER_ID,
            query=user_input,
            # top_k=MEMORY_RETRIEVAL_TOP_K
        )
        memory_text = ""
        if memory_results:
            memory_text = "\n".join(
                    f"Memory: {m.content.parts[0].text}" for m in memory_results if (hasattr(m, "content") and hasattr(m.content, "parts")
                                        and isinstance(m.content.parts, list)
                                        and len(m.content.parts) > 0
                                        and hasattr(m.content.parts[0], "text"))
            )

        # 3. Build sliding window context
        sliding_window = conversation_history[-SLIDING_WINDOW_SIZE:]
        sliding_window_text = "\n".join(sliding_window)

        # 4. (Optional) Summarize earlier context if conversation is long
        summary_text = ""
        if len(conversation_history) > SLIDING_WINDOW_SIZE:
            # For demo, just join earlier turns (replace with real summarization if needed)
            summary_text = "Summary of earlier conversation:\n" + "\n".join(conversation_history[:-SLIDING_WINDOW_SIZE])

        # 5. Combine all context
        combined_prompt = ""
        if summary_text:
            combined_prompt += summary_text + "\n\n"
        if memory_text:
            combined_prompt += f"Relevant past memories:\n{memory_text}\n\n"
        combined_prompt += f"Recent conversation:\n{sliding_window_text}\n\n"
        combined_prompt += f"Current question: {user_input}"

        # 6. Send to agent
        user_message = Content(parts=[Part(text=combined_prompt)], role="user")
        runner = Runner(
            agent=agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service
        )
        async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=user_message):
            if event.is_final_response():
                response = event.content.parts[0].text
                print("Agent:", response)
                conversation_history.append(f"Agent: {response}")
                break

        # 7. Store the session to memory for future retrieval
        completed_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session.id)
        await memory_service.add_session_to_memory(completed_session)

if __name__ == "__main__":
    asyncio.run(main())