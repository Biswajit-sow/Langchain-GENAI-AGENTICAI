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

agent = create_agent(
    model=ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1),
    tools=[send_email],
    system_prompt="You are an email assistant. Always use the send_email tool.",
)