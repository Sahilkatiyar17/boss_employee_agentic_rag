import streamlit as st
from services.api_client import call_rag_api   # later separate endpoint

def render():
    st.header("🏢 Boss–Employee Agent System")

    task = st.text_input("Enter task for Boss Agent")

    if st.button("Run Multi-Agent System"):
        if not task:
            st.warning("Please enter a task")
            return

        with st.spinner("Agents working..."):
            result = call_rag_api(task)   # 🔴 temp reuse

        st.success("Final Output")
        st.write(result)
