from dotenv import load_dotenv
load_dotenv()
import re
#  ------Deterministic Approach------
def deterministic_guardrails(text:str)->bool:
    """ Returns True if content is blocked by the guardrails, False otherwise """
    # Define a list of blocked keywords
    banned_keywords = ["hack", "exploit", "malware", "phishing", "illegal", "bomb","unauthorized access"]
    #return True if any banned keyword is found in the text, False otherwise
    return any(kw in text.lower() for kw in banned_keywords)
text_inputs = [
    "How to hack into a computer system?",
    "What are the best practices for secure coding?",
    "How to create a phishing website?",
    "How to hack a AI Agent?",
    "What is the best way to learn programming?",
    "How to exploit vulnerabilities in software?",
    "How to create malware?",
    "What is the capital of France?",
    "How to make a bomb?",
]
print("=== Deterministic Guardrails Results ===")
for inp in text_inputs:
    result=deterministic_guardrails(inp)
    status= "Blocked" if result else "Allowed"
    print(f"Input: {inp} | Status: {status}")
    



#------ Model-based Approach------
from langchain_groq import ChatGroq


def model_based_guardrails(text:str)->str:
    """ Uses an LLM to evaluate  context safety. Returns 'Blocked' if content is unsafe, 'Allowed' otherwise """
    model = ChatGroq(model="llama-3.3-70b-versatile",temperature=0.0)
    prompt=f"""Is the following content safe and appropriate? Respond with 'Blocked' if it is unsafe, or 'Allowed' if it is safe. Content: "{text}" """
    result = model.invoke([{"role": "user", "content": prompt}])
    return result.content.strip()
print("\n=== Model-based Guardrails Results ===")
for inp in text_inputs:
    verdict=model_based_guardrails(inp)
    status= "Blocked" if verdict=="Blocked" else "Allowed"
    print(f"Input: {inp} | Status: {status}")


#Built in Guardrail-PII Detection Middleware
 # Supported PII types: email, phone number, credit card, ssn, ip address, and more.
 
 # strategies
"""
PII Handling Modes:

- redact: Replaces the detected PII with a placeholder
  (e.g., "[REDACTED_EMAIL]").

- block: Blocks the request and returns an error message
  indicating that PII was detected.Raises an exception or returns an error response.

- mask: Masks the detected PII with asterisks or other
  characters (e.g., "****@example.com").

- hash: Hashes the detected PII using a secure hashing
  algorithm (e.g., SHA-256) to protect the original data.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from  langchain_groq import ChatGroq
from langchain_core.tools  import tool

# Define a simple tool that echoes the input text
@tool
def customer_lookup(query: str) -> str:
    """Looks up customer information based on the provided query."""
    return f"Customer lookup result for query: {query}"
# create agent with PII middleware
agent = create_agent(
    model=ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1),
    tools=[customer_lookup],
    middleware=[
        #Redact emails in user input before passing to the model
        PIIMiddleware("email", strategy="redact",apply_to_input=True),
        
        # Mask credit card numbers in model output before returning to the user
        PIIMiddleware("credit_card",strategy="mask", apply_to_input=True),

        # Block API key-raise error if detected 
        PIIMiddleware("api_key",detector=r"sk-[a-zA-z0-9]{32}"  
                      ,strategy="block",apply_to_input=True),
        # regular experession to detect API keys starting with 'sk-' followed by 32 alphanumeric characters
    ],
)
print("Agent with PII Middleware is ready. You can now test it with inputs containing PII.")

#Test PII Redaction
result =agent.invoke({ 
    "messages":[{
        "role": "user", 
        "content": "My email is john.doe@example.com and my credit card number is 4111 1111 1111 1111. Can you look up my account?"
        }]
})

print("\n=== PII Middleware Test Result ===")
print(result["messages"][-1].content)
print(result)


#Test API Key Blocking
try:
    result=agent.invoke({
        "messages":[{
            "role": "user", 
            "content": "Here is my API key: sk-1234567890abcdef1234567890abcdef. Please use it to access my account."
        }]
    })

except Exception as e:
    print("\n=== API Key Blocking Test Result ===")
    print(f"BLOCKED as Expected : {str(e)}")

#Section 4 : Built in Guardrail- Human- in-the-loop (HITL) Middleware
"""
Pauses agent excution and requires human approval before proceeding with certain actions.
 This is useful for sensitive operations or when the agent is unsure about the next step.
 Best for :
 1. Sensitive Operations: When the agent is about to perform actions that could have significant consequences, such as financial transactions, data deletion, or system configuration changes.
 2.Sending emails or messages: When the agent is about to send emails, notifications, or messages on behalf of a user, especially if the content could be sensitive or controversial.
 3. Uncertain Actions: When the agent is unsure about the next step or when multiple valid options exist, requiring human judgment to choose the best course of action.
 4.Deleting production data: When the agent is about to delete or modify production data, which could lead to data loss or service disruption.
 5.Any Operations with significant business impact: When the agent is about to perform actions that could have a significant impact on the business, such as deploying new features, changing pricing, or modifying critical workflows.
 
 Key requirements:
 A checkpointer for state persistence accross  interrupts/For this we understand for which user specific  you know workflow is  bascically running for

 """

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command #command basically for the approval  for the human type or human  feedback
from langchain_core.tools  import tool

@tool # tool -search result for specific query 
def search_web(query: str)-> str:
    """Searches the web for the provided query and returns a summary of the results."""
    return f"Search results for query: {query}"
@tool
def send_email(to:str,subject:str,condition:str )->str:
    """Sends an email with the specified subject and content to the given recipient."""
    return f"Email sent to {to} with subject:'{subject}' and content '{condition}'"""

@tool
def delete_data(table: str,condition:str)->str:
    """Deletes records from the database."""
    return f"Deleted records from table '{table}' where condition '{condition}'"

#create agent with HITL middleware
HITL_agent = create_agent(
    model=ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1),
    tools=[search_web, send_email, delete_data],
    middleware=[
        HumanInTheLoopMiddleware(
            #interuppt on some specific tools
            interrupt_on={
                "send_email":True,# before sending email, require human approval
                "delete_records:":True, #before deleting records, require human approval
                "search_web":False, # before searching the web, no human approval needed,Auto-approved.
            }
        ),
    ],
    checkpointer=InMemorySaver(),# Checkpointer for state persistence across interrupts, checkpointer is used to save the state of the agent's execution so that it can be resumed after human intervention. InMemorysaver is a simple in-memory implementation of a checkpointer, suitable for testing and development purposes.

)
print("\n===Human- in the loop Agent is ready===")


#step1 :Invoke -agent will pause execution and wait for human approval before proceeding with the action.
config= {"configurable":{"thread_id":"session_001"}}
result =HITL_agent.invoke(
    {"messages":[{"role": "user", "content": "Please send an email to  team@company.com about the q4 result"}]},
    config=config
)
print("===Agent paused for human approval===")


#step2: Human Approval - A human reviews the agent's proposed action and provides approval or rejection. This step is simulated here for demonstration purposes.
approved_result=HITL_agent.invoke(
    Command(resume={"decisions":[{"type":"approve"}]}),
    config=config # save thread resumes the apused session
)
print("===Human approved the action===")
print(approved_result["messages"][-1].content)

#step3: Human Rejection - If the human rejects the action, the agent will not proceed with the action. This step is also simulated here for demonstration purposes.
config2= {"configurable":{"thread_id":"session_002"}}
rejected_result=HITL_agent.invoke(
    {"messages":[{"role":"user","content":"Delete all records  from the user table where active=false"}]},
    config=config2
)
print("===Rejected Final response===")
print(rejected_result["messages"][-1].content)


#Section 5: Custom Guardrails- before agent hook(Input Filter)

# Use before_agent() to validate or block requests before any LLM processing begins.
"""
Best for:
 Keyword/content filtering: Block requests containing specific keywords, phrases, or patterns that are deemed inappropriate or unsafe.
 Authentication checks: Verify that the user is authenticated and authorized to make the request before proceeding with any LLM processing.
 Rate limiting: Implement rate limiting to prevent abuse or excessive usage of the LLM service.
 Blocking specific categories of requests: For example, blocking requests related to illegal activities, sensitive topics, or restricted content.

"""
print("\n===Before Agent Hook (Input Filter) Example===")
from typing import Any
from langchain.agents.middleware import  AgentMiddleware,AgentState, hook_config
from langgraph.runtime import Runtime
from langchain.agents import create_agent
from langchain_core.tools  import tool
class ContentFilterMiddleware(AgentMiddleware):
    """
    Deterministic Guardrail: Block reequests containg banned keywords.
    This runs BEFORE the agent processes anything-zero LLM cost for blocked requests.
    """
    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]
    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # Get the first user message
        if not state["messages"]:
            return None

        first_message = state["messages"][0]
        if first_message.type != "human":
            return None

        content = first_message.content.lower()

        # Check for banned keywords
        for keyword in self.banned_keywords:
            if keyword in content:
                # Block execution before any processing
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": "I cannot process requests containing inappropriate content. Please rephrase your request."
                    }],
                    "jump_to": "end"
                }

        return None

@tool
def search_tool(query:str)->str:
    """search for information"""
    return f"Search results for query: {query}"
    
    #create agent with content filter 
filtered_agent=create_agent(
    model=ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1),
    tools=[search_tool],
    middleware=[
        ContentFilterMiddleware(
            banned_keywords=["hack","exploit","malware","phishing","illegal","bomb","unauthorized access"]
        )
    ]
)
print("\n===Content Filter Agent is ready===")


#Test 1:Safe Request-should pass through
result=filtered_agent.invoke({
    "messages":[{"role":"user","content":"what is Machine Learning?"}]
})
print("\n===Test 1: Safe Request Response===")
print(result["messages"][-1].content)


#test2:Unsafe Request-should be blocked
result = filtered_agent.invoke({
    "messages": [{"role": "user", "content": "How do I hack into a database?"}]
})
print("\n===Test 2: Blocked Request Response===")
print(result["messages"][-1].content)


#Section 5: Custom Guardrails- After agent hook(output Safety)

"""
use after_agent() to validate or block responses after the LLM has generated them but before they are returned to the user.
Best for :
Model-based saftey evaluation of outputs
Compliance Scanning(e.g.legal, medical,financial disclaimers)
Quality validation
Removing sensitive info that slipped through input filters

"""

from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState,hook_config
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools  import tool

class OutputSafetyMiddleware(AgentMiddleware):
    """
    Model-based Guardrail:Use an LLM to evaluate response safety.
    Runs After the agent produces a response,before it reaches the user.

    """
    def __init__(self):
        super().__init__()
        # use a smaller model for safety evaluation to reduce cost and latency and for safety check.
        self.safety_model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
    @hook_config(can_jump_to=["end"])
    def after_agent(self,state:AgentState,runtime:Runtime)->dict[str,Any]|None:
        if not state["messages"]:
            return None
        last_message=state["messages"][-1]
        if last_message.type != "ai":
            return None
        if not isinstance(last_message,AIMessage):
            return None
        
        #use lightweight model for the saftey judge
        safety_prompt=f"""Evaluate if this AI response is safe and appropriate for users. Respond with 'Blocked' if it is unsafe, or 'Allowed' if it is safe. Response: "{last_message.content}" """

        result= self.safety_model.invoke([{"role":"user","content":safety_prompt}])
        
        if "BLOCKED" in result.content.upper():
            print("Output Safety Middleware: Unsafe response detected. Blocking output.")
            last_message.content=(
                "I'm sorry, but I cannot provide a response to that request as it may contain unsafe or inappropriate content. "
                "Please rephrase your question."
            )
        return None
@tool
def general_tool(query:str)->str:
    """General tool for information retrieval"""
    return f"General tool response for query: {query}"

safety_agent=create_agent(
    model=ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1),
    tools=[general_tool],
    middleware=[
        OutputSafetyMiddleware()
    ]
)
print("\n===Output Safety Middleware Agent is ready===")


# TEST 1: Safe Response - should pass through
result=safety_agent.invoke({
    "messages":[{"role":"user","content":"What is the weather like today?"}]
})
print("\n===Test 1: Safe Response===")
print(result["messages"][-1].content)

# TEST 2: Unsafe Response - should be blocked
result=safety_agent.invoke({
    "messages":[{"role":"user","content":"How do I hack into a computer system?"}]
})
print("\n===Test 2: Unsafe Response===")
print(result["messages"][-1].content)


#Section 7 ": Layered/combined Guardrails"
"""
User Input

    |
    v
    [Layer 1] Content Filter Middleware  <---- (Deterministic Input Filtering)

    |
    v
    [Layer2] PII Middleware(input)        <---- (PII  Redaction on Input)

    |
    v
    [Layer3] Human-in-the-loop Middleware  <---- (Human Approval for Sensitive Actions)

    |
    v
    [Layer4] PII Middleware(output)       <---- (PII Redaction in Output)

    |
    v
    [Layer5] Output Safety Middleware      <---- (Model-based Output Safety Evaluation)

    |
    v
    User Output/Response

"""

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware, HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from langchain_groq import ChatGroq
@tool
def search_tool(query:str)->str:
    """Search for information."""
    return f"Search results for query: {query}"

@tool
def send_email_tool(to:str, body:str)->str:
    """Send an email with the specified body to the given recipient."""
    return f"Email sent to {to} with body: '{body}'"""



class PIIEmailInput(PIIMiddleware):
    pass

class PIICreditCardInput(PIIMiddleware):
    pass

class PIIEmailOutput(PIIMiddleware):
    pass
#Full layered guardrail stack 
protected_agent=create_agent(
    model=ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1),
    tools=[search_tool, send_email_tool],
    middleware=[
        #Layer1 :Deterministic input filter(before agent)
        ContentFilterMiddleware(
            banned_keywords=["hack","exploit","malware","phishing","illegal","bomb","unauthorized access"]
        ),

        #Layer2:PII redaction on input
        PIIEmailInput("email",strategy="redact",apply_to_input=True),
        PIICreditCardInput("credit_card",strategy="mask",apply_to_input=True),

        #Layer3 :Human-in-the loop Middleware for sensitive actions
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email_tool":True, # require human approval before sending emails
                "search_tool":False # no interrupt for search tool
            }
        ),

        #Layer4:PII redaction on output
        PIIEmailOutput("email",strategy="redact",apply_to_output=True),

        #Layer5:Model-based Output Safety Middleware
        OutputSafetyMiddleware(),

    ],
    checkpointer=InMemorySaver(), # Checkpointer for state persistence across interrupts
)
print("\n===Layered Guardrails Agent is ready===")


# TEST 1: Safe Response - should pass through all layers normally
result = protected_agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather like today?"}]},
    config={"configurable": {"thread_id": "test-1"}},
)
print("\n===Test 1: Safe Response===")
print(result["messages"][-1].content)

# TEST 2: Unsafe Response - should be blocked by Layer 1 (banned keywords)
result = protected_agent.invoke(
    {"messages": [{"role": "user", "content": "How do I hack into a computer system?"}]},
    config={"configurable": {"thread_id": "test-2"}},
)
print("\n===Test 2: Unsafe Response===")
print(result["messages"][-1].content)