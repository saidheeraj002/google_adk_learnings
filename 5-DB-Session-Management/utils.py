from google.genai import types

async def display_state(session_service, app_name, user_id, session_id):
    session = session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    # Handle the user name
    user_name = session.state.get("user_name", "Unknown")
    print(f"👤 User: {user_name}")

    # Handle reminders
    preferences = session.state.get("user_Preferences", [])
    if preferences:
        print("📝 preferences:")
        for idx, preferences in enumerate(preferences, 1):
            print(f"  {idx}. {preferences}")
    else:
        print("📝 preferences: None")

async def call_agent_async(runner, user_id, session_id, query):
    new_message = types.Content(role="user", parts=[types.Part(text=query)])

    print("===================== State Before Processing the Request ===============================")

    await display_state(runner.session_service, runner.app_name, user_id, session_id)

    print("===================== **************** ===============================")

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
                print(f"Final Response: {event.content.parts[0].text}")

    
    print("===================== State After Processing the Request ===============================")

    await display_state(runner.session_service, runner.app_name, user_id, session_id)

    print("===================== **************** ===============================")

    return final_response





    


