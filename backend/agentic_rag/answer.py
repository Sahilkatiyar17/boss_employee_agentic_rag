from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

answer_llm = ChatGroq(model="openai/gpt-oss-120b")

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
