from google.adk.agents import SequentialAgent
from assesment_agent.sub_agents.mcq_assesment_generation_agent.agent import mcq_assement_generation_agent
from assesment_agent.sub_agents.retriever_agent.agent import make_retriever_agent

mcq_generation_pipeline = SequentialAgent(
    name="MCQ_Generation_Pipeline",
    sub_agents=[make_retriever_agent(), mcq_assement_generation_agent],
    description="A pipeline that retrieves the content on the user query and generates the MCQ Assesment paper.",
)