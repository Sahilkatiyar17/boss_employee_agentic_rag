# frontend/app.py
import streamlit as st

st.set_page_config(
    page_title="Agentic AI System",
    layout="wide"
)

st.title("🤖 Agentic AI Playground")

from pages.boss_employee import render
render()
