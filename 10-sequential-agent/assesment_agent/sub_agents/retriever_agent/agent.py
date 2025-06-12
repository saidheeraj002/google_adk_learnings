from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from vertexai.language_models import TextEmbeddingModel
from pinecone import Pinecone


def retrieve_content(user_query:str, tool_context: ToolContext) -> dict:
    """Use this ONLY to retrieve information for the user asked query"
            "(Physics, Chemistry, Maths, etc.) from the knowledge base. "
            "The input to this tool MUST be a string containing query."
            "with the Pinecone filter conditions (dictionary).

    Args:
        query: The user asked query.
        tool_context: Context for accessing session state and updating session state        
    
    Return:
        Retrieved Content information.
    """
    print("=========================================================================================")
    print("this is a retirever agent call")
    print("User Query:", user_query)
    top_k = 5

    embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    query_embeddings = embedding_model.get_embeddings([user_query])
    query_vector = query_embeddings[0].values  # or .embedding, depending on the API

    pinecone_client = Pinecone(api_key="pcsk_4gQsLN_PDNbGoZbjStT8sqdPSCyrTJMvz6rnULgJyJzbmQrMhCnVtHj34apJK4B7xPSgpC")
    pinecone_index = pinecone_client.Index("12-maths-text-book")

    results = pinecone_index.query(
            vector=query_vector,
            top_k=top_k,
            filter={"chapter_name": {"$in": ["Matrices", "Application Of Derivatives", "Determinants", "Relations And Functions", "Inverse Trigonometry Functions", 
                                             "Continuity And Differentiability", "Integrals", "Application Of Integrals",
                                             "Differential Equations", "Vector Algebra", "Three Dimensional Geometry", "Linear Programming", "Probability"]}},
            include_values=False,
            include_metadata=True,
            rerank={
                "model": "bge-reranker-v2-m3",  # Ensure this model is available/configured
                "top_n": top_k,  # Rerank the initially retrieved top_k results
                "rank_fields": ["chunk_text"]  # Field containing text for reranking
           }
        )
    
    content =  [match.metadata["text"] for match in results.matches]
    print("retrieved_content", content)
    print("#####################################################################################################")

    tool_context.state['retrieved_content'] = content

    return {
        "action": "retrieving_the_content",
        "retrieved_content": content,
    }


def make_retriever_agent():
    return LlmAgent(
    name="retriever_agent",
    model="gemini-2.0-flash",
    description="Retrieve the Content based on the user query.",
    instruction="""
        You are a **Retriever Agent** in an intelligent educational system designed to support automatic assessment generation.
        When the user asks a question, use the retrieve_content tool and pass their message as the user_query argument.

        Your task is to retrieve accurate, complete, and relevant textbook content based solely on the user’s input query. The retrieved content will be used by an Assessment Generation Agent to generate multiple choice questions.

        <user_request>
        query: {user_query}   # A topic, concept, chapter name, or general request provided by the user.
        </user_request>

        ---

        ### 🔍 Your Responsibilities:

        1. **Analyze the user's query** to determine the appropriate retrieval scope:
        - If the query clearly specifies a particular question from the chapter, then Retrieve only question.
        - If the query clearly specifies a single topic or chapter, retrieve all relevant content for that chapter or topic.
        - If the query suggests multiple topics or chapters, retrieve content covering all specified areas.
        - If the query is broad or general (e.g., "entire textbook," "all chapters on geometry"), retrieve the corresponding comprehensive content.

        2. **Retrieve content strictly from the official textbook or curriculum corpus.**

        3. **Ensure completeness and factual accuracy**, including definitions, formulas, examples, and explanations relevant to the user’s query.

        4. **Avoid adding any interpretation, summaries, or unrelated information.**

        ---

        ### ✅ Output Format:

        Return the retrieved content wrapped exactly as follows:

        <retrieved_content>
        Content:
        {retrieved_content}
        </retrieved_content>

        ---

        ### 🚫 Important Constraints:

        - Do not invent or hallucinate information.
        - Do not paraphrase or summarize; provide original textbook content.
        - Do not include partial or irrelevant content.
        - Do not add commentary or additional notes.

        Your output must be **ready-to-use textbook material**, fully aligned with the user's implicit scope, to support accurate and effective assessment question generation.
    """,
    tools=[retrieve_content]
)