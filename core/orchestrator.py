from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

def route_query(user_prompt: str, chat_history: list) -> str:
    """Routes the query to the correct domain agent using a local LLM."""
    
    # Connect to your local Ollama instance (Make sure 'ollama run llama3' was executed previously)
    llm = ChatOllama(model="llama3", temperature=0)
    
    # We use prompt engineering to force the local model to reply with a single word
    system_prompt = """You are the routing engine for the SRH University AI Copilot.
    Analyze the user's prompt and categorize it into exactly ONE of the following categories:
    - TEACHING: For course design, rubrics, learning objectives, CORE principle, teaching methods.
    - HR: For contracts, freelancer documents, compliance, external lecturers.
    - CAREER: For CV reviews, cover letters, job applications, student jobs.
    - GENERAL: For anything else.
    
    Reply ONLY with the category word (TEACHING, HR, CAREER, or GENERAL). Do not include any other text or punctuation.
    """
    
    # Get the routing decision
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    # The model should return just the word (e.g., "TEACHING")
    decision = llm.invoke(messages).content.strip().upper()
    
    print(f"DEBUG: Orchestrator routed to -> {decision}") # Helpful for testing
    
    # Dispatch to the correct agent
    if "TEACHING" in decision:
        from agents.teaching_agent.agent import run_teaching_agent
        return run_teaching_agent(user_prompt)
    elif "HR" in decision:
        return "🛠️ [Routing to HR Agent]: I am analyzing the HR compliance request... (WIP by Teammate 1)"
    elif "CAREER" in decision:
        return "🛠️ [Routing to Career Agent]: Let's look at your CV... (WIP by Teammate 2)"
    else:
        return f"I am the general assistant. You asked: {user_prompt}"