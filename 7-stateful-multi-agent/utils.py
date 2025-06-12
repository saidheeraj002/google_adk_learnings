from google.genai import types
from datetime import datetime


async def update_interaction_history(session_service, app_name, user_id, session_id, entry):
    try:
        # Get current session
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # Get current interaction history
        interaction_history = session.state.get("interaction_history", [])

        # Add timestamp if not already present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the entry to interaction history
        interaction_history.append(entry)

        # Create updated state
        updated_state = session.state.copy()
        updated_state["interaction_history"] = interaction_history

        # Create a new session with updated state
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=updated_state,
        )
    except Exception as e:
        print(f"Error updating interaction history: {e}")


async def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    """Add a user query to the interaction history."""
    await update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "user_query",
            "query": query,
        },
    )


async def add_agent_response_to_history(
    session_service, app_name, user_id, session_id, agent_name, response):
    """Add an agent response to the interaction history."""
    await update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "agent_response",
            "agent": agent_name,
            "response": response,
        },
    )


async def display_state(session_service, app_name, user_id, session_id):
    session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    user_name = session.state.get("user_name", "Unknown")
    print(f"User: {user_name}")

    booked_tickets = session.state.get("tickets_booked", [])

    if booked_tickets and any(booked_tickets):
        print("Tickets Booked:")
        for tickets in booked_tickets:
            course_id = tickets.get("id", "Unknown")
            purchase_date = tickets.get("purchase_date", "Unknown date")
            print(f"  - {course_id} (purchased on {purchase_date})")

    interaction_history = session.state.get("interaction_history", [])
    if interaction_history:
        print("📝 Interaction History:")
        for idx, interaction in enumerate(interaction_history, 1):
            # Pretty format dict entries, or just show strings
            if isinstance(interaction, dict):
                action = interaction.get("action", "interaction")
                timestamp = interaction.get("timestamp", "unknown time")

                if action == "user_query":
                    query = interaction.get("query", "")
                    print(f'  {idx}. User query at {timestamp}: "{query}"')
                elif action == "agent_response":
                    agent = interaction.get("agent", "unknown")
                    response = interaction.get("response", "")
                    # Truncate very long responses for display
                    if len(response) > 100:
                        response = response[:97] + "..."
                    print(f'  {idx}. {agent} response at {timestamp}: "{response}"')
                else:
                    details = ", ".join(
                        f"{k}: {v}"
                        for k, v in interaction.items()
                        if k not in ["action", "timestamp"]
                    )
                    print(
                        f"  {idx}. {action} at {timestamp}"
                        + (f" ({details})" if details else "")
                    )
            else:
                print(f"  {idx}. {interaction}")
    else:
        print("📝 Interaction History: None")


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

    # Check for specific parts first
    has_specific_part = False
    # if event.content and event.content.parts:
    #     for part in event.content.parts:
    #         if hasattr(part, "text") and part.text and not part.text.isspace():
    #             print(f"  Text: '{part.text.strip()}'")

    # Check for final response after specific parts
    # final_response = None
    # print("event", event)
    # print("event_content", event.content)
    # if not has_specific_part and event.is_final_response():
    #     if (
    #             event.content
    #             and event.content.parts
    #             and event.content.parts[0].text.strip()
    #     (sad)
    #         final_response = event.content.parts[0].text.strip()
    #         # Use colors and formatting to make the final response stand out
    #         print(
    #             "╔══ AGENT RESPONSE ═════════════════════════════════════════"
    #         )
    #         print(f"{final_response}")
    #         print(
    #             "╚═════════════════════════════════════════════════════════════\n"
    #         )
    #     else:
    #         print(
    #             "==> Final Agent Response: [No text content in final event]\n"
    #         )
    return final_response


async def call_agent_async(runner, user_id, session_id, query):
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = None
    agent_name = None

    # Display state before processing the message
    await display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
    )
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

    if final_response_text and agent_name:
        await add_agent_response_to_history(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            agent_name,
            final_response_text,
        )

    await display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
    )

    return final_response_text