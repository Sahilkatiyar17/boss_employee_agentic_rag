import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import TokenTextSplitter
from langchain_groq import ChatGroq
from langchain_experimental.graph_transformers import LLMGraphTransformer


load_dotenv()









NEO4J_URI = os.environ["NEO4J_URI"] 
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"] 
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"] 


graph = Neo4jGraph()




# 1. Initialize the loader with the path to your file
loader = PyPDFLoader(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\sodapdf-converted.pdf")

# 2. Load the data into Document objects
# This returns a list: [Document(page_content='...', metadata={'source': '...', 'page': 0}), ...]
docs = loader.load()

# Example: Accessing the first page
#print(docs[0].page_content[:100])


text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
documents = text_splitter.split_documents(docs[:3])


llm = ChatGroq(model="openai/gpt-oss-120b")
llm_transformer = LLMGraphTransformer(llm=llm)


graph_documents = llm_transformer.convert_to_graph_documents(documents)

graph.add_graph_documents(
    graph_documents,
    baseEntityLabel=True,
    include_source=True
)

