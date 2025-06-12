from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from datetime import datetime


def new_ticket_booking(movie_name: str, tool_context: ToolContext) -> dict:
    """
    Simulates the Booking of Movie Ticket.
    Updates the State with the Booked Ticket Details.
    :param movie_name:
    :param tool_context:
    :return:
    """
    print("movie_name", movie_name)
    movie_name = movie_name
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    booked_tickets = tool_context.state.get("tickets_booked", [])

    booked_movie_name = [
        movie["movie_name"] for movie in booked_tickets if isinstance(booked_tickets, dict)
    ]
    if movie_name in booked_movie_name:
        return {"status": "error", "message": "You have already booked the ticket to this Movie!"}

    new_movie_bookings = []

    for movie in booked_tickets:
        if isinstance(movie, dict) and "movie_name" in movie:
            new_movie_bookings.append(movie)

    new_movie_bookings.append({"movie_name": movie_name, "purchase_date": current_time})

    tool_context.state["tickets_booked"] = new_movie_bookings

    current_interaction_history = tool_context.state.get("interaction_history", [])

    new_interaction_history = current_interaction_history.copy()
    new_interaction_history.append(
        {"action": "ticket_booking", "movie_info": movie_name, "timestamp": current_time}
    )

    tool_context.state["interaction_history"] = new_interaction_history

    return {
        "status": "success",
        "message": "Successfully Booked the Ticket!",
        "movie_ifo": movie_name,
        "timestamp": current_time,
    }


def view_all_tickets_booked(tool_context: ToolContext) -> dict:
    """
        View all Booked Tickets List of Movies

        Args:
            tool_context: Context for accessing session state

        Returns:
            This is the List of Tickets Booked.
        """
    list_of_tickets_booked = tool_context.state.get("tickets_booked", [])

    return {"action": "view_tickets_booked", "ticket_booked_info": list_of_tickets_booked}


ticket_booking_agent = Agent(
    name="ticket_booking_agent",
    model="gemini-2.0-flash",
    description="Ticket Booking Agent For the User Selected/Chosen Movie",
    instruction="""
        You are a Ticket Booking Agent, specifically handles the booking of the ticket for the user preferred Movies.
        
        <user_info>
        Name: {user_name}
        </user_info>
    
        <movies_info>
        Movies Info List: {movies_info_list}
        </movies_info>
    
        <interaction_history>
        {interaction_history}
        </interaction_history>
        
        Movie Details:
        - Movie Name: Any Movie name that user is selected.
        - Price: $100.
        
        When Interacting with the user:
        1. Check if the user is already booked the ticket for the movie i.e., that he is asking to book.
            - Booked Movie Information will be stored as a object with tickets_booked state with movie_name and booked_date
        
        2. If they have already Booked the ticket for the Movie.
            - Remind them the Ticket is already booked for the mentioned movie.
            - Direct them to the Movies Info list.
            
        3. After any interaction:
            - The state will automatically track the interaction 
        
        Remember:
            - Be helpful but not pushy
            - Focus on the value and practical skills they'll gain
            - Emphasize the hands-on nature of building a real AI application
    """,
    tools=[new_ticket_booking, view_all_tickets_booked]
)