from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

# -----------------------------
# 1. RAW DOCUMENTS (TEXT ONLY)
# -----------------------------

documents = [
    "Executive Summary Q1 2024: Overall revenue grew steadily driven by SmartX Watch adoption in urban regions. Leadership emphasized balancing growth with supply chain stability.",

    "CEO Strategy Note: The company aims to position SmartX as a premium yet accessible smart wearable brand, focusing on health tracking and lifestyle integration.",

    "Board Meeting Insight: Expansion in South India remains a priority due to strong smartwatch demand, while North India continues to lead headset sales.",

    "Long-Term Vision Document: SmartX plans to evolve from a hardware-focused company into a data-driven health and lifestyle ecosystem.",

    "Q1 2024 Sales Summary: SmartX Headsets performed strongest in North India, while SmartX Watch sales increased significantly in South India.",

    "Regional Sales Analysis: West India showed moderate adoption across all wearable categories but demonstrated higher repeat customer behavior.",

    "Sales Team Observation: Fitness Bands sell better in semi-urban markets due to affordability and simpler feature requirements.",

    "Revenue Commentary: Seasonal promotions contributed to short-term revenue spikes but did not significantly impact long-term customer retention.",

    "Marketing Strategy Note: Instagram and influencer-based campaigns improved headset visibility among the 18-25 age group.",

    "Campaign Review: Smartwatch ads focusing on heart rate tracking and sleep monitoring achieved higher engagement rates than generic lifestyle ads.",

    "Growth Team Insight: Customer acquisition costs are higher in urban regions but result in better lifetime value.",

    "Brand Positioning Discussion: Marketing leadership agreed to shift messaging from 'smart gadget' to 'health companion'.",

    "Product Roadmap: SmartX plans to launch SmartX Pro Headset and SmartX Health Watch in the next fiscal year.",

    "Product Team Note: Customers increasingly expect longer battery life and better sensor accuracy across all wearables.",

    "Design Review Summary: SmartX Watch design improvements were prioritized based on user comfort feedback.",

    "Feature Planning Document: Advanced sleep analytics and stress monitoring are under evaluation for future releases.",

    "Operational Note: Inventory shortages were observed in South India due to supplier delays in sensor components.",

    "Supply Chain Review: Dependency on a single sensor supplier increases operational risk during peak demand periods.",

    "Warehouse Report: Northern warehouses maintained healthy stock levels, reducing delivery delays.",

    "Operations Strategy: Leadership recommended diversifying suppliers to reduce future inventory disruptions.",

    "Customer Feedback Summary: SmartX Watch users praised health tracking features but reported occasional syncing issues.",

    "Support Team Note: Headset users frequently request better noise cancellation in high-traffic environments.",

    "User Research Insight: Fitness Band customers prioritize simplicity and battery life over advanced analytics.",

    "Customer Sentiment Analysis: Brand trust improved after transparent communication regarding shipment delays.",

    "Internal Sales Meeting: Teams discussed improving cross-selling strategies between headsets and smartwatches.",

    "Marketing-Sales Sync Notes: Agreement reached on aligning campaign launches with product availability.",

    "Leadership Decision Log: Inventory risk management assigned as a cross-functional responsibility.",

    "Quarterly Review Meeting: Emphasis placed on data-driven decision making using unified company datasets.",

    "Risk Assessment: Over-reliance on urban markets may limit long-term growth opportunities.",

    "Operational Learning: Delayed supplier communication directly impacted regional fulfillment timelines.",

    "Market Insight: Competitive pressure is increasing in the smartwatch segment due to aggressive pricing by new entrants.",

    "Post-Mortem Summary: Early forecasting inaccuracies contributed to uneven inventory distribution."
]

# --------------------------------
# 2. CONVERT TO DOCUMENT OBJECTS
# --------------------------------

docs = [Document(page_content=text) for text in documents]

# --------------------------------
# 3. CHUNKING (IMPORTANT)
# --------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
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
    "boss-employee-agentic-rag/backend/data/chroma"
)

vector_store = Chroma.from_documents(
    documents=chunked_docs,
    embedding=embeddings,
    persist_directory=persist_directory,
    collection_name="company_docs"
)



print("✅ Vector store created and persisted successfully")
