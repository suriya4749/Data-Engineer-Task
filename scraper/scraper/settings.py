import logging
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()

BOT_NAME = "scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

logging.getLogger("pymongo").setLevel(logging.ERROR)

# -------------------
# MongoDB configs (Docker service name or env override)
# -------------------
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://host.docker.internal:27017"  # fallback for local machine
)
MONGO_DATABASE = os.getenv("MONGO_DB", "identity_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "profiles")
DUPLICATES_COLLECTION = os.getenv("DUPLICATES_COLLECTION", "profiles_duplicates")

# -------------------
# Neo4j configs (Docker service name or env override)
# -------------------
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "newpassword")

# -------------------
# Proxy settings
# -------------------
PROXY_TOKEN = os.getenv("PROXY_TOKEN", "5aa93984046948219deed2b41b2315996fc654e8be4")
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "True").lower() == "true"
PROXY_URL = f"http://{PROXY_TOKEN}:@proxy.scrape.do:8080"

DOWNLOADER_MIDDLEWARES = {
    'scraper.middlewares.ProxyMiddleware': 350,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = {
    "scraper.custom_pipelines.cleanup_pipeline.CleanupPipeline": 300,
    "scraper.custom_pipelines.scoring_pipeline.ScoringPipeline": 300,
    "scraper.pipelines.MongoPipeline": 400,
}

FEED_EXPORT_ENCODING = "utf-8"
