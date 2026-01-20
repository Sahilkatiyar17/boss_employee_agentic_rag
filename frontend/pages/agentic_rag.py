import streamlit as st
from services.api_client import call_rag_api

def render():
    st.header("📚 Agentic RAG")

    query = st.text_input("Ask a question")

    if st.button("Run Agent"):
        if not query:
            st.warning("Please enter a question")
            return

        with st.spinner("Agent is thinking..."):
            answer = call_rag_api(query)

        st.success("Answer")
        st.write(answer)
