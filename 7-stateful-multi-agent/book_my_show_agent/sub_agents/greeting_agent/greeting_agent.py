from google.adk.agents import Agent

greeting_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description=("Greeting Agent"),
    instruction=(
        "You are a greeting agent which greets the user very politely."
    ),
)