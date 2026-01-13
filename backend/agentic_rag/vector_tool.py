from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --------------------------------
# LOAD VECTOR STORE ONCE
# --------------------------------

persist_directory = (
    "F:/sahil/2025-2026/Project_DS/"
    "boss-employee-agentic-rag/backend/data/chroma"
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings,
    collection_name="company_docs"
)

# --------------------------------
# VECTOR TOOL FUNCTION
# --------------------------------

def run_vector(intent: dict) -> str:
    """
    intent example:
    {
        "topics": [
            "inventory shortage",
            "South India",
            "supply delay"
        ]
    }
    """

    topics = intent.get("topics", [])
    query = " ".join(topics)

    if not query:
        return ""

    docs = vectorstore.similarity_search(
        query=query,
        k=5
    )

    return "\n".join(
        [doc.page_content for doc in docs]
    )

intent = {
        "topics": [
            "inventory shortage",
            "South India",
            "supply delay"
        ]
    }

print(run_vector(intent))