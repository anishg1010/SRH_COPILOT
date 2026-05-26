from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

def run_teaching_agent(user_prompt: str) -> str:
    """
    This is the CORE-Empowerment Bot.
    Running completely locally via Ollama.
    """
    # Using temperature=0.7 for more creative teaching suggestions
    llm = ChatOllama(model="llama3", temperature=0.7)
    
    system_prompt = """
    You are the SRH CORE-Empowerment Bot (Teaching Innovation Agent).
    You help lecturers design competence-oriented courses, generate learning objectives, 
    and design assessments.
    
    [MOCK MODE]: Since you don't have access to the SRH PDFs yet, provide a highly 
    professional, generic pedagogical answer based on modern higher education standards. 
    Mention that you are applying the 'CORE principle'. Keep your answer concise and well-formatted.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    # Generate the response
    response = llm.invoke(messages)
    
    return "🎓 **[CORE Teaching Agent (Local Model)]**\n\n" + response.content