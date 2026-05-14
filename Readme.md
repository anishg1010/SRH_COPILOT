University AI CO-PILOT
srh-copilot/
├── .env.example                # Template for API keys (OpenAI, etc.)
├── requirements.txt            # Shared dependencies
├── README.md                   # Project instructions
├── main.py                     # Entry point for the Orchestrator/App
│
├── frontend/                   # Streamlit or web interface UI files
│   └── app.py
│
├── core/                       # Shared AI Services & Data Layer
│   ├── orchestrator.py         # The routing engine to direct user queries
│   ├── rag_pipeline.py         # Shared chunking and retrieval logic
│   └── database.py             # Vector DB connection setup
│
├── data/                       # Knowledge & Data Layer (Ignore in .gitignore)
│   ├── core_docs/              # Put your LINC/Teaching PDFs here
│   ├── hr_forms/
│   └── faqs/
│
└── agents/                     # Specialized Domain Agents (Team workspaces)
    ├── teaching_agent/         # YOUR WORKSPACE
    │   ├── __init__.py
    │   ├── agent.py            # Logic for the CORE Bot
    │   └── prompts.py          # Pedagogical system prompts
    ├── hr_agent/               # Teammate 1's workspace
    ├── career_agent/           # Teammate 2's workspace
    └── analytics_agent/        # Teammate 3's workspace






1st meeting discussion
1. What exact problem are we solving first?
2. Which use case has highest priority?
3. Who is the primary user ?
4. Do you need only the prototype or the final product as well?
5. What about the Dataset?
6. where can we find the documents? 
7. what type of output expected for different agents? 
8. what will be the source of Input? 
9. Everyone should have access to all the agents or specific type of people will have access to specific agents?