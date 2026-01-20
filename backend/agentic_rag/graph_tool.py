"""
Advanced Graph Retrieval Tool for Neo4j GraphRAG
Implements hybrid retrieval strategies with proper error handling,
relationship filtering, and fallback mechanisms.
"""

import os
import logging
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# CONFIGURATION
# =========================
load_dotenv()

# Neo4j connection with retry logic
try:
    graph = Neo4jGraph()
    logger.info("✓ Neo4j connection established successfully")
except Exception as e:
    logger.error(f"✗ Failed to connect to Neo4j: {e}")
    graph = None

# Vector store configuration
PERSIST_DIRECTORY = r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\graph_chroma"
FULLTEXT_INDEX_NAME = "entity"  # Name of your fulltext index in Neo4j

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Chroma vector store
try:
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_name="company_docs"
    )
    logger.info("✓ Vector store loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load vector store: {e}")
    vectorstore = None

# =========================
# NODE/RELATIONSHIP MAPPINGS
# =========================
# Define your specific node types and relationships based on your schema
ALLOWED_NODE_LABELS = [
    "Activity", "Agerange", "Brand", "City", "Company", "Component",
    "Concept", "Customer", "Customersegment", "Datasource", "Date",
    "Demographic", "Department", "Development", "Document", "Employeecount",
    "Entity", "Feature", "Group", "Industry"
]

# Define relationship types based on your use case
# You can customize this based on question patterns
RELATIONSHIP_CONTEXT_MAPPING = {
    "features": ["HAS_FEATURE", "FEATURE", "HAS_COMPONENT"],
    "demographics": ["HAS_DEMOGRAPHIC", "AGE_RANGE"],
    "location": ["BASED_IN"],
    "employees": ["EMPLOYEES"],
    "development": ["DEVELOPED_WITH"],
    "accuracy": ["ACHIEVED_ACCURACY", "ACCURACY"],
    "collaboration": ["COLLABORATED_WITH"],
    "feedback": ["HAS_FEEDBACK"],
    "engagement": ["ENGAGES_WITH"],
    "default": []  # Empty list means all relationships
}

# =========================
# UTILITY FUNCTIONS
# =========================
def safe_node_identifier(node: Dict[str, Any]) -> str:
    """
    Extract a readable identifier from a Neo4j node.
    Tries multiple common property names.
    """
    for key in ["name", "title", "id", "value", "description"]:
        if key in node and node[key]:
            value = str(node[key])
            return value if len(value) <= 100 else f"{value[:97]}..."
    return "<unknown>"


def generate_fulltext_query(text: str, fuzzy: bool = True) -> str:
    """
    Generate a Lucene-compatible fulltext query string.
    
    Args:
        text: Raw search text
        fuzzy: Enable fuzzy matching with ~2 distance
    
    Returns:
        Formatted fulltext query
    """
    words = [w for w in remove_lucene_chars(text).split() if w and len(w) > 2]
    if not words:
        return ""
    
    if fuzzy:
        # Use fuzzy matching for better recall
        return " AND ".join(f"{w}~2" for w in words)
    else:
        # Exact matching
        return " AND ".join(words)


def detect_query_context(question: str) -> List[str]:
    """
    Analyze the question to determine which relationships are most relevant.
    Returns a list of relationship types to filter on.
    """
    question_lower = question.lower()
    
    for context_key, relationships in RELATIONSHIP_CONTEXT_MAPPING.items():
        if context_key in question_lower:
            logger.info(f"Detected context: {context_key} -> Relationships: {relationships}")
            return relationships
    
    # Default: return empty list (all relationships)
    logger.info("No specific context detected, using all relationships")
    return RELATIONSHIP_CONTEXT_MAPPING["default"]


def build_traversal_cypher(
    allowed_rels: Optional[List[str]] = None,
    depth: int = 1,
    return_format: str = "detailed"
) -> str:
    """
    Build the Cypher query for graph traversal after fulltext search.
    
    Args:
        allowed_rels: List of relationship types to filter on (None = all)
        depth: Traversal depth (1 or 2 recommended)
        return_format: "simple" or "detailed"
    
    Returns:
        Cypher query string for RETURN clause
    """
    # Node identifier expressions
    node_id = "coalesce(node.name, node.title, node.id, elementId(node))"
    neighbor_id = "coalesce(neighbor.name, neighbor.title, neighbor.id, elementId(neighbor))"
    
    if return_format == "simple":
        # Simple format: just node-relationship-neighbor triples
        if not allowed_rels or len(allowed_rels) == 0:
            return f"""
            MATCH (node)-[r]-(neighbor)
            WHERE neighbor IS NOT NULL
            WITH node, type(r) as relType, collect(DISTINCT {neighbor_id})[..5] as neighbors
            RETURN {node_id} + ' [' + relType + '] ' + 
                   reduce(s = '', n IN neighbors | s + n + ', ') AS output
            LIMIT 10
            """
        else:
            rels = "|".join(allowed_rels)
            return f"""
            MATCH (node)-[r:{rels}]-(neighbor)
            WHERE neighbor IS NOT NULL
            WITH node, type(r) as relType, collect(DISTINCT {neighbor_id})[..5] as neighbors
            RETURN {node_id} + ' [' + relType + '] ' + 
                   reduce(s = '', n IN neighbors | s + n + ', ') AS output
            LIMIT 10
            """
    
    else:  # detailed format
        # Include node labels and properties
        if not allowed_rels or len(allowed_rels) == 0:
            return f"""
            MATCH (node)-[r]-(neighbor)
            WHERE neighbor IS NOT NULL
            WITH node, r, neighbor
            RETURN 
                labels(node)[0] + ':' + {node_id} + 
                ' --[' + type(r) + ']-- ' + 
                labels(neighbor)[0] + ':' + {neighbor_id} AS output
            LIMIT 15
            """
        else:
            rels = "|".join(allowed_rels)
            return f"""
            MATCH (node)-[r:{rels}]-(neighbor)
            WHERE neighbor IS NOT NULL
            WITH node, r, neighbor
            RETURN 
                labels(node)[0] + ':' + {node_id} + 
                ' --[' + type(r) + ']-- ' + 
                labels(neighbor)[0] + ':' + {neighbor_id} AS output
            LIMIT 15
            """


# =========================
# CORE RETRIEVAL FUNCTIONS
# =========================
def graph_retriever(
    question: str,
    top_k: int = 3,
    relationship_filter: Optional[List[str]] = None,
    auto_detect: bool = True
) -> str:
    """
    Retrieve context from Neo4j graph using fulltext index and traversal.
    
    Args:
        question: User's question
        top_k: Number of initial nodes to retrieve via fulltext
        relationship_filter: Specific relationships to traverse (None = all)
        auto_detect: Automatically detect relevant relationships from question
    
    Returns:
        Formatted context string
    """
    if not graph:
        logger.warning("Graph connection not available, falling back to vector store")
        return ""
    
    # Generate fulltext query
    query_text = generate_fulltext_query(question, fuzzy=True)
    if not query_text:
        logger.warning("Empty fulltext query generated")
        return ""
    
    # Auto-detect relationships if enabled
    if auto_detect and relationship_filter is None:
        relationship_filter = detect_query_context(question)
    
    # Build traversal query
    traversal_cypher = build_traversal_cypher(
        allowed_rels=relationship_filter,
        depth=1,
        return_format="detailed"
    )
    
    # Complete Cypher query
    full_query = f"""
    CALL db.index.fulltext.queryNodes($index_name, $query, {{limit: $top_k}})
    YIELD node, score
    {traversal_cypher}
    """
    
    try:
        logger.info(f"Executing graph query with: {query_text}")
        results = graph.query(
            full_query,
            {
                "index_name": FULLTEXT_INDEX_NAME,
                "query": query_text,
                "top_k": top_k
            }
        )
        
        if not results:
            logger.info("No results from graph query")
            return ""
        
        # Extract and format outputs
        outputs = [row.get("output", "") for row in results if row.get("output")]
        context = "\n".join(outputs)
        
        logger.info(f"Retrieved {len(outputs)} graph results")
        return context
        
    except Exception as e:
        logger.error(f"Graph query error: {e}")
        logger.debug(f"Query parameters: query_text={query_text}, top_k={top_k}")
        return ""


def vector_retriever(query: str, top_k: int = 3) -> str:
    """
    Retrieve context from Chroma vector store as fallback.
    
    Args:
        query: User's question
        top_k: Number of documents to retrieve
    
    Returns:
        Formatted context string
    """
    if not vectorstore:
        logger.error("Vector store not available")
        return ""
    
    try:
        docs = vectorstore.similarity_search(query, k=top_k)
        context = "\n\n".join(doc.page_content for doc in docs)
        logger.info(f"Retrieved {len(docs)} vector results")
        return context
    except Exception as e:
        logger.error(f"Vector retrieval error: {e}")
        return ""


def hybrid_retriever(
    query: str,
    graph_top_k: int = 3,
    vector_top_k: int = 2,
    relationship_filter: Optional[List[str]] = None
) -> str:
    """
    Combine graph and vector retrieval for comprehensive context.
    
    Args:
        query: User's question
        graph_top_k: Number of graph results
        vector_top_k: Number of vector results
        relationship_filter: Relationships to filter on in graph
    
    Returns:
        Combined context string
    """
    graph_context = graph_retriever(
        query,
        top_k=graph_top_k,
        relationship_filter=relationship_filter
    )
    
    vector_context = vector_retriever(query, top_k=vector_top_k)
    
    # Combine contexts
    contexts = []
    if graph_context:
        contexts.append("=== Graph Knowledge ===\n" + graph_context)
    if vector_context:
        contexts.append("=== Document Context ===\n" + vector_context)
    
    return "\n\n".join(contexts)


# =========================
# MAIN ENTRY POINT
# =========================
def get_graph_context(
    question: str,
    strategy: str = "auto",
    **kwargs
) -> str:
    """
    Main entry point for retrieving context.
    
    Args:
        question: User's question
        strategy: "graph", "vector", "hybrid", or "auto"
        **kwargs: Additional parameters for specific retrievers
    
    Returns:
        Retrieved context string
    """
    logger.info(f"Retrieving context with strategy: {strategy}")
    
    try:
        if strategy == "graph":
            result = graph_retriever(question, **kwargs)
            if result.strip():
                logger.info("✓ Graph retrieval successful")
                return result
            else:
                logger.info("Graph retrieval empty, falling back to vector")
                return vector_retriever(question)
                
        elif strategy == "vector":
            return vector_retriever(question, **kwargs)
            
        elif strategy == "hybrid":
            return hybrid_retriever(question, **kwargs)
            
        else:  # auto strategy
            # Try graph first
            result = graph_retriever(question, **kwargs)
            if result.strip():
                logger.info("✓ Using graph context")
                return result
            else:
                # Fallback to vector
                logger.info("→ Falling back to vector context")
                return vector_retriever(question)
                
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        # Ultimate fallback
        try:
            return vector_retriever(question)
        except Exception as fallback_error:
            logger.error(f"Fallback retrieval also failed: {fallback_error}")
            return ""


# =========================
# HEALTH CHECK
# =========================
def health_check() -> Dict[str, bool]:
    """Check if all components are functioning."""
    status = {
        "graph_db": False,
        "vector_store": False,
        "fulltext_index": False
    }
    
    # Check Neo4j
    if graph:
        try:
            graph.query("RETURN 1")
            status["graph_db"] = True
            
            # Check fulltext index
            index_check = graph.query(
                f"SHOW INDEXES WHERE name = '{FULLTEXT_INDEX_NAME}'"
            )
            status["fulltext_index"] = len(index_check) > 0
            
        except Exception as e:
            logger.error(f"Graph health check failed: {e}")
    
    # Check vector store
    if vectorstore:
        try:
            vectorstore.similarity_search("test", k=1)
            status["vector_store"] = True
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
    
    return status


# =========================
# TEST & EXAMPLES
# =========================
if __name__ == "__main__":
    print("=" * 60)
    print("GraphRAG Tool - Health Check")
    print("=" * 60)
    
    status = health_check()
    for component, is_healthy in status.items():
        print(f"  {component}: {'✓ OK' if is_healthy else '✗ FAILED'}")
    
    print("\n" + "=" * 60)
    print("Testing Retrieval")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "When did Smartx watch launch?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        context = get_graph_context(query, strategy="auto")
        if context:
            print(context[:300] + "..." if len(context) > 300 else context)
        else:
            print("No context retrieved")
        print()