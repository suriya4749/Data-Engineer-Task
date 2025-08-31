import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapy import signals
from pymongo import MongoClient
from scraper.loaders.neo4j_loader import Neo4jLoader

class Neo4jSpiderSignals:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def spider_closed(self, spider):
        client = MongoClient("mongodb://mongo:27017")
        db = client["profiles_db"]
        profiles = db["profiles"]

        loader = Neo4jLoader(
            neo4j_uri="bolt://neo4j:7687",
            neo4j_user="neo4j",
            neo4j_password="newpassword"
        )

        for profile in profiles.find({}):
            loader.load_profile(profile)

        loader.close()
        client.close()
        print("All profiles loaded into Neo4j successfully!")
