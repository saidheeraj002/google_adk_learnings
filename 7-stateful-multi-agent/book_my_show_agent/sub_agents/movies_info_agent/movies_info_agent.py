from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def add_new_movie(movie_info: str, tool_context: ToolContext) -> dict:
    """
    Add a New Movie to the movies_info_list

    Args:
        movie_info: The Movie Info to add
        tool_context: Context for accessing session state and updating session state

    Return:
        A Confirmation Message
    """
    print(f"--- Tool: add_new_movie called for '{movie_info}' ----")

    movie_info_list = tool_context.state.get("movies_info_list", [])
    movie_info_list.append(movie_info)

    tool_context.state["movies_info_list"] = movie_info_list

    return {
        "action": "add_new_movie",
        "new_movie_info": movie_info,
        "message": f"Added New Movie: {movie_info_list}"
    }


def list_movies_info(tool_context: ToolContext) -> dict:
    """
    View all Current List of Movies

    Args:
        tool_context: Context for accessing session state

    Returns:
        This is the List of Movies
    """
    movies_info = tool_context.state.get("movies_info_list", [])

    return {"action": "view_movies_info", "movies_info": movies_info}


movies_info_agent = Agent(
    name="movies_info_agent",
    model="gemini-2.0-flash",
    description="Movies Info Agent",
    instruction="""
        You are a Movie Info provider agent for the List of Movies available.
        Your role is to help the user to provide the list
        
        <user_info>
        Name: {user_name}
        </user_info>
    
        <movies_info>
        Movies Info: {movies_info_list}
        </movies_info>
    """,
    tools=[list_movies_info, add_new_movie]
)