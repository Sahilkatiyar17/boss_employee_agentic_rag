import streamlit as st
from services.api_client import call_rag_api

def render():
    st.header("📚 Agentic RAG")

    query = st.text_input("Ask a question")

    if "rag_answer" not in st.session_state:
        st.session_state.rag_answer = None

    if st.button("Run Agent"):
        if not query:
            st.warning("Please enter a question")
            return

        with st.spinner("Agent is thinking..."):
            try:
                st.session_state.rag_answer = call_rag_api(query)
            except Exception as e:
                st.error(f"API error: {e}")
                st.session_state.rag_answer = None

    if st.session_state.rag_answer is not None:
        st.success("Answer")
        st.write(st.session_state.rag_answer.get("response", st.session_state.rag_answer))
