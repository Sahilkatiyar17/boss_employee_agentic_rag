import streamlit as st
from services.api_client import call_rag_api   # later separate endpoint

def render():
    st.header("🏢 Boss–Employee Agent System")

    task = st.text_input("Enter task for Boss Agent")

    if "boss_answer" not in st.session_state:
        st.session_state.boss_answer = None

    if st.button("Run Multi-Agent System"):
        if not task:
            st.warning("Please enter a task")
            return

        with st.spinner("Agents working..."):
            try:
                st.session_state.boss_answer = call_rag_api(task)   # 🔴 temp reuse
            except Exception as e:
                st.error(f"API error: {e}")
                st.session_state.boss_answer = None

    if st.session_state.boss_answer is not None:
        st.success("Final Output")
        st.write(st.session_state.boss_answer.get("response", st.session_state.boss_answer))
