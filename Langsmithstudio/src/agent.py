from langchain.agents import create_agent
from langchain_groq import ChatGroq


def send_email(to: str, subject: str, body: str):
    """Send an email"""
    email = {
        "to": to,
        "subject": subject,
        "body": body
    }
    # ... email sending logic

    return f"Email sent to {to}"


def search_web(query: str):
    """Search the web for up-to-date information"""
    # ... real search logic (Tavily, SerpAPI, etc.) goes here
    return f"Top results for '{query}': [stub result 1, stub result 2]"


def create_calendar_event(title: str, date: str, time: str):
    """Create a calendar event. date is YYYY-MM-DD, time is HH:MM"""
    # ... real calendar API call goes here
    return f"Event '{title}' created for {date} {time}"


def calculate(expression: str):
    """Evaluate a basic arithmetic expression, e.g. '2 * (3 + 4)'"""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: expression contains disallowed characters."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error evaluating expression: {e}"


agent = create_agent(
    model=ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1),
    tools=[send_email, search_web, create_calendar_event, calculate],
    system_prompt=(
        "You are a general-purpose assistant. You have tools for sending "
        "email, searching the web, creating calendar events, and doing "
        "calculations. Use a tool whenever the request requires one. If "
        "required info is missing, ask the user instead of guessing."
    ),
)