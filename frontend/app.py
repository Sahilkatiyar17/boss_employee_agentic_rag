# frontend/app.py
import streamlit as st

st.set_page_config(
    page_title="Agentic AI System",
    layout="wide"
)

st.title("🤖 Agentic AI Playground")

# Sidebar navigation
page = st.sidebar.radio(
    "Select Mode",
    ["Agentic RAG", "Boss–Employee Agent"]
)

if page == "Agentic RAG":
    from pages.agentic_rag import render
    render()

elif page == "Boss–Employee Agent":
    from pages.boss_employee import render
    render()
