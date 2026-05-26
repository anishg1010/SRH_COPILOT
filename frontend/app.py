import streamlit as st
import sys
import os

# Ensure the app can find your local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.orchestrator import route_query

st.set_page_config(page_title="SRH AI Copilot", page_icon="🎓")

st.title("SRH University AI Copilot 🎓")
st.caption("Intelligent Support for Teaching, HR, Career, and Services")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to the SRH Copilot! How can I help you today?"}
    ]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("E.g., Help me design a grading rubric..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from the Orchestrator
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # This calls the router you will build in Step 4
            response = route_query(prompt, st.session_state.messages)
            st.markdown(response)
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})