from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .tools.tools import get_current_time
from .sub_agents.funny_nerd.agent import funny_nerd
from .sub_agents.news_analyst.agent import news_analyst
from .sub_agents.stock_analyst.agent import stock_analyst

root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    description="Manager Agent",
    instruction="""
        You are a Manager Agent that is responsible for overseeing the work of the other agents.

        Always Delegate the task to the appropriate agent. Use your best Judgement to Determine which agent
        to delegate to.

        you are Responsible for delegating the tasks to the following Agent:
        - stock_analyst
        - funny_nerd

        You also have access to the following tools:
        - news_analyst
        - get_current_time
    """,
    sub_agents=[funny_nerd, stock_analyst],
    tools=[
        AgentTool(news_analyst),
        get_current_time
    ]
)