from google.adk.agents import LlmAgent

MODEL = "gemini-2.0-flash"

agent = LlmAgent(
    model=MODEL,
    name="SmartMemoryAgent",
    instruction=(
        "You are a helpful assistant. Use the recent conversation and any relevant past memories provided to answer the user's question."
    )
)