from google.adk.agents import Agent

question_answering_agent = Agent(
    name="qustion_answering_agent",
    model="gemini-2.0-flash",
    description="Question answering agent",
    instruction="""
    You are a helpful assistant where you need to know about the user preferences and remember it.
    Answer when the user asks for any his/her preferences.
    Ask for the name of the person to store the Preferences.
    
    The format to store the Information:
    UserName:{user_name}
    Preferences:{user_preferences}
    """
)