from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.orchestrator import handle_user_query


st.set_page_config(page_title="SRH AI Copilot", page_icon="🎓")

st.title("SRH AI Copilot")
st.subheader("LINC Agent - Lecturer Support")

query = st.text_area("Ask a teaching or course design question:")

if st.button("Ask LINC"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking with tiny academic gears..."):
            answer = handle_user_query(query)
        st.markdown(answer)