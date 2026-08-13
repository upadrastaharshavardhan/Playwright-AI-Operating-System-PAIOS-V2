from neo4j import AsyncGraphDatabase
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class Neo4jClient:
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            await self._driver.verify_connectivity()
            logger.info("Neo4j connection established")

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")

    async def run(self, query: str, parameters: dict = None):
        async with self._driver.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()

    async def create_knowledge_node(self, label: str, properties: dict):
        query = f"CREATE (n:{label} $props) RETURN n"
        return await self.run(query, {"props": properties})

    async def create_relationship(self, from_id: str, to_id: str, rel_type: str, props: dict = None):
        query = f"""
        MATCH (a), (b)
        WHERE id(a) = $from_id AND id(b) = $to_id
        CREATE (a)-[r:{rel_type} $props]->(b)
        RETURN r
        """
        return await self.run(query, {"from_id": from_id, "to_id": to_id, "props": props or {}})

    async def get_agent_knowledge_graph(self, agent_id: str):
        query = "MATCH (a:Agent {id: $agent_id})-[r]-(n) RETURN a, r, n"
        return await self.run(query, {"agent_id": agent_id})

    async def search_knowledge(self, query_text: str, limit: int = 10):
        query = """
        CALL db.index.fulltext.queryNodes('knowledge', $query_text)
        YIELD node, score
        RETURN node, score
        LIMIT $limit
        """
        return await self.run(query, {"query_text": query_text, "limit": limit})
