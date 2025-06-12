from google.adk.agents import SequentialAgent
from assesment_agent.sub_agents.question_paper_generation_agent.agent import question_paper_generation_agent
from assesment_agent.sub_agents.retriever_agent.agent import make_retriever_agent

question_paper_generation_pipeline = SequentialAgent(
    name="Question_Paper_Generation_Pipeline",
    sub_agents=[make_retriever_agent(), question_paper_generation_agent],
    description="A pipeline that retrieves the content on the user query and generates the Assesment Question Paper.",
)