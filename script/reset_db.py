from pymongo import MongoClient
from neo4j import GraphDatabase

# -----------------------------
# MongoDB setup
# -----------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["profiles_db"]

# Collections
profiles = db["profiles"]
duplicates = db["profiles_duplicates"]

# -----------------------------
# Neo4j setup
# -----------------------------
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "newpassword"   # your updated password
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))


def reset_mongo():
    """Clear MongoDB collections."""
    print("Deleting all existing profiles from MongoDB...")
    profiles.delete_many({})
    print("Deleting all duplicate profiles from MongoDB...")
    duplicates.delete_many({})
    print("MongoDB reset complete.")


def reset_neo4j():
    """Clear Neo4j database (all nodes & relationships)."""
    with driver.session() as session:
        print("Deleting all nodes and relationships from Neo4j...")
        session.run("MATCH (n) DETACH DELETE n")
        print("Neo4j reset complete.")


def reset_db():
    """Clear all profile data for a fresh crawl in both MongoDB & Neo4j."""
    reset_mongo()
    reset_neo4j()
    print("Database reset complete. You can start a fresh crawl.")


if __name__ == "__main__":
    reset_db()
    driver.close()
