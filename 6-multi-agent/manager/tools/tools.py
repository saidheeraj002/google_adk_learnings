from datetime import datetime

def get_current_time() -> dict:
    """
        Get the Current Date Time in the format YYYY-MM-DD HH:MM:SS
    """

    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }