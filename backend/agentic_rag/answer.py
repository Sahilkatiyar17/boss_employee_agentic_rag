from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os  
load_dotenv()
AGENTIC_API_KEY = os.environ["AGENTIC_API_KEY"]
answer_llm = ChatGroq(model="openai/gpt-oss-120b", api_key=AGENTIC_API_KEY)

def generate_answer(query, context):
    return answer_llm.invoke(
        f"""
Answer the question strictly using the context below.

Question:
{query}

Context:
{context}
"""
    ).content
