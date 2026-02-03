from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

PDF_PATHS = [
    r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\Smart_Tech_Technologies.pdf",
    r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\SmartTech_Business_Report_FY2024.pdf",
]

PERSIST_DIRECTORY = (
    r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\chroma"
)

COLLECTION_NAME = "company_docs"

# -------------------------------------------------
# 1. LOAD BOTH PDFs (ONLY THESE TWO)
# -------------------------------------------------

all_docs = []

for pdf_path in PDF_PATHS:
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    pdf_name = pdf_path.split("\\")[-1]

    for doc in docs:
        doc.metadata.update({
            "source_pdf": pdf_name,
            "company": "OurCompany",
            "document_type": "internal_report",
            "confidence": "high"
        })

    all_docs.extend(docs)

print(f"✅ Loaded {len(all_docs)} pages from 2 PDFs")

# -------------------------------------------------
# 2. CHUNKING
# -------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunked_docs = text_splitter.split_documents(all_docs)

print(f"✅ Created {len(chunked_docs)} chunks")

# -------------------------------------------------
# 3. EMBEDDINGS
# -------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -------------------------------------------------
# 4. INJECT INTO EXISTING CHROMA COLLECTION
# -------------------------------------------------

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIRECTORY
)

vector_store.add_documents(chunked_docs)


print("✅ Both PDFs successfully injected into ChromaDB")
