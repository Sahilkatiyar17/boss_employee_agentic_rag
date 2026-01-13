from neo4j import GraphDatabase

# Connect to Neo4j
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "gy35Dy3NJW-5oWGTPNVGPu9I1A0gKgioZy5qvcqfq0o"))

def create_graph(tx):

    # Products
    tx.run("""
    MERGE (:Product {name:'SmartX Headset', category:'Headset', lifecycle:'Growth'})
    MERGE (:Product {name:'SmartX Watch', category:'Smartwatch', lifecycle:'Growth'})
    MERGE (:Product {name:'SmartX Fitness Band', category:'Band', lifecycle:'New'})
    """)

    # Departments
    tx.run("""
    MERGE (:Department {name:'Sales'})
    MERGE (:Department {name:'Marketing'})
    MERGE (:Department {name:'SupplyChain'})
    """)

    # Regions
    tx.run("""
    MERGE (:Region {name:'North India', market:'Urban'})
    MERGE (:Region {name:'South India', market:'Urban'})
    MERGE (:Region {name:'West India', market:'Semi-Urban'})
    """)

    # Suppliers
    tx.run("""
    MERGE (:Supplier {name:'TechComponents Ltd', type:'Sensors'})
    """)

    # Features
    tx.run("""
    MERGE (:Feature {name:'Heart Rate Tracking'})
    MERGE (:Feature {name:'Noise Cancellation'})
    """)

    # Issues
    tx.run("""
    MERGE (:Issue {type:'Inventory Delay', severity:'Medium'})
    """)

    # Customer Segments
    tx.run("""
    MERGE (:CustomerSegment {name:'Fitness Enthusiasts'})
    MERGE (:CustomerSegment {name:'Office Professionals'})
    """)

    # Datasets
    tx.run("""
    MERGE (:Dataset {name:'Sales_DB', type:'SQL'})
    MERGE (:Dataset {name:'Marketing_DB', type:'SQL'})
    MERGE (:Dataset {name:'Company_Knowledge', type:'Vector'})
    """)

    # Relationships
    tx.run("""
    MATCH (p:Product {name:'SmartX Watch'}), (f:Feature {name:'Heart Rate Tracking'})
    MERGE (p)-[:HAS_FEATURE]->(f)
    """)

    tx.run("""
    MATCH (p:Product {name:'SmartX Watch'}), (s:CustomerSegment {name:'Fitness Enthusiasts'})
    MERGE (p)-[:TARGETS]->(s)
    """)

    tx.run("""
    MATCH (p:Product {name:'SmartX Watch'}), (i:Issue {type:'Inventory Delay'})
    MERGE (p)-[:AFFECTED_BY]->(i)
    """)

    tx.run("""
    MATCH (i:Issue {type:'Inventory Delay'}), (d:Department {name:'SupplyChain'})
    MERGE (d)-[:RESPONDS_TO]->(i)
    """)

    tx.run("""
    MATCH (p:Product {name:'SmartX Watch'}), (ds:Dataset {name:'Sales_DB'})
    MERGE (p)-[:RELATED_TO_DATASET]->(ds)
    """)
    


with driver.session() as session:
    session.execute_write(create_graph)

driver.close()
print("Graph DB setup completed!")