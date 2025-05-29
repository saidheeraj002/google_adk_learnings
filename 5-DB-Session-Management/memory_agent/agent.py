from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

def add_preference(preference: str, tool_context: ToolContext) -> dict:
    """Add a New Preference to the user's preference List

    Args:
        preference: The preference text to add
        tool_context: Context for accessing and updating session state

    Returns:
        A confirmation message
    """
    print(f"--- Tool: add_preference called for '{preference}' ---")

    # Get current reminders from state
    preferences = tool_context.state.get("user_Preferences", [])

    # Add the new reminder
    preferences.append(preference)

    # Update state with the new list of reminders
    tool_context.state["user_Preferences"] = preferences

    return {
        "action": "add_preferences",
        "reminder": preference,
        "message": f"Added preferences: {preferences}",
    }

def view_preferences(tool_context: ToolContext) -> dict:
    """View all current preferences.

    Args:
        tool_context: Context for accessing session state

    Returns:
        The list of preferences
    """
    print("--- Tool: view_preferences called ---")

    # Get reminders from state
    preferences = tool_context.state.get("user_Preferences", [])

    return {"action": "view_preferences", "preferences": preferences, "count": len(preferences)}



memory_agent = Agent(
    name="memory_agent",
    model="gemini-2.0-flash",
    description="A Smart Agent which remembers the user Preferences with Persistant Memory.",
    instruction="""
        You are a friendly Assistant that remembers the Users Movie Preferences.

        The users information is stored in state:
        User's name: {user_name}
        Preferences: {user_Preferences}

        You can help users remember their preferences with the following capabilities:
        1. Add new preferences
        2. View existing preferences
        3. Update preferences
        4. Delete preferences
        5. Update the user's name

        Always be friendly and address the user by name. If you don't know their name yet,
        use the update_user_name tool to store it when they introduce themselves.

        **Preferences MANAGEMENT GUIDELINES:**
    
    When dealing with preferences, you need to be smart about finding the right preference:
    
    1. When the user asks to update or delete a preference but doesn't provide an index:
       - If they mention the content of the preference (e.g., "delete my preference"), 
         look through the preferences to find a match
       - If you find an exact or close match, use that index
       - Never clarify which preference the user is referring to, just use the first match
       - If no match is found, list all preferences and ask the user to specify
    
    2. When the user mentions a number or position:
       - Use that as the index (e.g., "delete reminder 2" means index=2)
       - Remember that indexing starts at 1 for the user
    
    3. For relative positions:
       - Handle "first", "last", "second", etc. appropriately
       - "First preference" = index 1
       - "Last preference" = the highest index
       - "Second preference" = index 2, and so on
    
    4. For viewing:
       - Always use the view_preferences tool when the user asks to see their preferences
       - Format the response in a numbered list for clarity
       - If there are no preferences, suggest adding some
    
    5. For addition:
       - Extract the actual preferences text from the user's request
       - Remove phrases like "add a preference to".
       - Focus on the task itself (e.g., "My preference is Game of Thrones")
    
    6. For updates:
       - Identify both which preference to update and what the new text should be
       - For example, "change my second preference to Prison Break" → update_reminder(2, "Prison Break")
    
    7. For deletions:
       - Confirm deletion when complete and mention which preference was removed
       - For example, "I've deleted your preference to 'Prison Break'"
    
    Remember to explain that you can remember their information across conversations.

    IMPORTANT:
    - use your best judgement to determine which preference the user is referring to. 
    - You don't have to be 100% correct, but try to be as close as possible.
    - Never ask the user to clarify which preference they are referring to.
    """,
    tools=[
        add_preference,
        view_preferences
    ],
)

