from google.genai import types
from datetime import datetime

async def process_agent_response(event):
    final_response = None
    if event.is_final_response():
        if event.content and event.content.parts:
            final_response = event.content.parts[0].text.strip()
            print(
                "╔══ AGENT RESPONSE ═════════════════════════════════════════"
            )
            print(f"{final_response}")
            print(
                "╚═════════════════════════════════════════════════════════════\n"
            )
    """Process and display agent response events."""
    print(f"Event ID: {event.id}, Author: {event.author}")

    return final_response


async def call_agent_async(runner, user_id, session_id, user_query):
    content = types.Content(role="user", parts=[types.Part(text=user_query)])

    input_dict = {"user_query": user_query}

    final_response_text = None
    agent_name = None

    try:
        async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content):
            # Capture the agent name from the event if available
            if event.author:
                agent_name = event.author

            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"ERROR during agent run: {e}")
    return final_response_text