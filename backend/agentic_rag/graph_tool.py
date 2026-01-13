from neo4j import GraphDatabase

class GraphTool:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    def close(self):
        self.driver.close()

    def run(self, intent: dict) -> str:
        """
        intent = {
            "entities": ["SmartX Watch", "South India"],
            "relations": ["SOLD_IN"]
        }
        """

        entities = intent.get("entities", [])
        relations = intent.get("relations", [])

        if not entities or not relations:
            return "No graph context required."

        relation = relations[0]  # Phase-1: single relation

        cypher = """
        MATCH (a)-[r:%s]->(b)
        WHERE a.name IN $entities OR b.name IN $entities
        RETURN a.name AS source, type(r) AS relation, b.name AS target
        """ % relation

        with self.driver.session() as session:
            result = session.run(cypher, entities=entities)
            records = result.data()

        if not records:
            return "No matching graph relationships found."

        context = []
        for r in records:
            context.append(
                f"{r['source']} {r['relation']} {r['target']}"
            )

        return "\n".join(context)


"""graph_tool = GraphTool(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="gy35Dy3NJW-5oWGTPNVGPu9I1A0gKgioZy5qvcqfq0o"
)

intent = {
    "entities": ["SmartX Watch",  "Heart Rate Tracking"],
    "relations": ["HAS_FEATURE"]
}

print(graph_tool.run(intent))"""


def run_graph(intent: dict) -> str:
    graph_tool = GraphTool(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="gy35Dy3NJW-5oWGTPNVGPu9I1A0gKgioZy5qvcqfq0o"
    )

    return graph_tool.run(intent)
