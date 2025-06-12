from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from datetime import datetime


def cancel_ticket(movie_name: str, tool_context: ToolContext) -> dict:
    """
    Simulates Cancelling ticket and refunding the amount for the movie user mentioned.
    Updates state by removing the Movie from tickets_booked.
    :param movie_name:
    :param tool_context:
    :return:
    """

    movie_name = movie_name
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    booked_tickets = tool_context.state.get("tickets_booked", [])

    booked_movie_name = [
        movie["movie_name"] for movie in booked_tickets if isinstance(booked_tickets, dict)
    ]
    if movie_name in booked_movie_name:
        return {"status": "error", "message": "You have not Booked any ticket to this Movie!"}

    new_movie_bookings = []
    for movie in booked_tickets:
        # Skip empty entries or non-dict entries
        if not movie or not isinstance(movie, dict):
            continue
        # Skip the course being refunded
        if movie.get("movie_name") == movie_name:
            continue
        # Keep all other courses
        new_movie_bookings.append(movie)

    tool_context.state["tickets_booked"] = new_movie_bookings

    current_interaction_history = tool_context.state.get("interaction_history", [])

    new_interaction_history = current_interaction_history.copy()
    new_interaction_history.append(
        {"action": "refund_amount", "movie_info": movie_name, "timestamp": current_time}
    )

    tool_context.state["interaction_history"] = new_interaction_history

    return {
        "status": "success",
        "message": """Successfully Cancelled the ticket and Refunded the amount.
         Your $149 will be returned to your original payment method within 3-5 business days.""",
        "movie_ifo": movie_name,
        "timestamp": current_time,
    }


ticket_cancel_agent = Agent(
    name="ticket_cancel_agent",
    model="gemini-2.0-flash",
    description="Cancel the Booked Ticket and refund the amount back to the user.",
    instruction="""
        Your role is to help users view their Booked Tickets History, and process refunds.
        
        <user_info>
        Name: {user_name}
        </user_info>
    
        <tickets_booked_movie_info>
        Tickets Booked: {tickets_booked}
        </tickets_booked_movie_info>
    
        <interaction_history>
        {interaction_history}
        </interaction_history>
        
        When users ask about cancelling the Ticket of a movie that they purchased:
        1. Check that Movie Ticket is purchased or not from the tickets_booked info above
            - Booked Ticket information is stored as objects with "movie_name" and "purchase_date" properties
        
        When users request a refund:
        1. Verify they have booked the ticket and they want to refund.
        2. If they Booked it:
           - Use the cancel_ticket tool to cancel and process the refund
           - Confirm the refund was successful
           - Remind them the money will be returned to their original payment method
           - If it's been more than 30 days, inform them that they are not eligible for a refund
        3. If the user didn't booked any ticket for the mentioned movie:
           - Inform them they didn't purchase the ticket for that movie, so no refund is needed.
        
        Example Response for Booked Tickets History:
        "Here are your Booked Tickets:
            - Movie Name: RRR
            - Purchased on: 2024-04-21 10:30:00
        
        Example Response for Refund:
        "I've processed your refund for the Movie you have mentioned to cancel.
        Your $100 will be returned to your original payment method within 3-5 business days.
        The Booked Ticket has been removed from your account."
    
        If they haven't Booked any Tickets:
        - Let them know they don't have any Tickets Booked.
        
        Remember:
        - Be clear and professional
        - Mention our 30-day money-back guarantee if relevant
    """,
    tools=[cancel_ticket]
)