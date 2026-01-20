from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import os

load_dotenv()

# -----------------------------
# 1. RAW DOCUMENTS (TEXT ONLY)
# -----------------------------

# 1. Initialize the loader with the path to your file
loader = PyPDFLoader(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\sodapdf-converted.pdf")

# 2. Load the data into Document objects
# This returns a list: [Document(page_content='...', metadata={'source': '...', 'page': 0}), ...]
docs = loader.load()


# --------------------------------
# 2. CONVERT TO DOCUMENT OBJECTS
# --------------------------------



# --------------------------------
# 3. CHUNKING (IMPORTANT)
# --------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=150
)

chunked_docs = text_splitter.split_documents(docs)

# --------------------------------
# 4. EMBEDDINGS
# --------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# --------------------------------
# 5. CHROMA VECTOR STORE
# --------------------------------

persist_directory = (
    "F:/sahil/2025-2026/Project_DS/"
    "boss_employee_agentic_rag/backend/data/graph_chroma"
)

vector_store = Chroma.from_documents(
    documents=chunked_docs,
    embedding=embeddings,
    persist_directory=persist_directory,
    collection_name="company_docs"
)



print("✅ Vector store created and persisted successfully")
