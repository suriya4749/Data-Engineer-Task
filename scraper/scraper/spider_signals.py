import sys, os
import logging
from scrapy import signals
from pymongo import MongoClient
from scraper.loaders.neo4j_loader import Neo4jLoader

# Optional: set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jSpiderSignals:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def spider_closed(self, spider):
        # -------------------
        # MongoDB config (dynamic)
        # -------------------
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://host.docker.internal:27017")
        mongo_db = os.environ.get("MONGO_DB", "profiles_db")
        mongo_collection = os.environ.get("MONGO_COLLECTION", "profiles")

        # -------------------
        # Neo4j config (dynamic)
        # -------------------
        neo4j_uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
        neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
        neo4j_password = os.environ.get("NEO4J_PASSWORD", "newpassword")

        # Connect to MongoDB
        logger.info(f"Connecting to MongoDB at {mongo_uri}, DB: {mongo_db}, Collection: {mongo_collection}")
        client = MongoClient(mongo_uri)
        db = client[mongo_db]
        profiles = db[mongo_collection]

        if profiles.count_documents({}) == 0:
            logger.warning("No profiles found in MongoDB. Skipping Neo4j load.")
            client.close()
            return

        # Connect to Neo4j
        loader = Neo4jLoader(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password
        )
        logger.info(f"Loading profiles into Neo4j at {neo4j_uri}...")

        try:
            for profile in profiles.find({}):
                loader.load_profile(profile)
            logger.info("All profiles loaded into Neo4j successfully!")
        except Exception as e:
            logger.error(f"Error loading profiles into Neo4j: {e}")
        finally:
            loader.close()
            client.close()
