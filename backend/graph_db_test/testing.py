from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "gy35Dy3NJW-5oWGTPNVGPu9I1A0gKgioZy5qvcqfq0o"))

def get_customer_purchases(tx, customer_name):
    result = tx.run("""
    MATCH (c:Customer {name:$name})-[:PURCHASED]->(p:Product)
    RETURN p.name AS product, c.name AS customer
    """, name=customer_name)
    return [(record["customer"], record["product"]) for record in result]

with driver.session() as session:
    purchases = session.execute_read(get_customer_purchases, "Amit Sharma")
    print(purchases)

driver.close()