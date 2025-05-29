from google.adk.agents import Agent

root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash-live-001",
    description=(
        "Greeting Agent"
    ),
    instruction=(
        "You are a helpful assistant that greets the user Ask the user's name and greet them by name."
    )
)