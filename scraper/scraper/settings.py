import logging
BOT_NAME = "scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

logging.getLogger("pymongo").setLevel(logging.ERROR)

# -------------------
# MongoDB configs (Docker service name)
# -------------------
MONGO_URI = "mongodb://mongo:27017"
MONGO_DATABASE = "identity_db"   # keep consistent
MONGO_COLLECTION = "profiles"
DUPLICATES_COLLECTION = "profiles_duplicates"

# -------------------
# Neo4j configs (Docker service name)
# -------------------
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "newpassword"

# -------------------
# Proxy settings
# -------------------
PROXY_TOKEN = "5aa93984046948219deed2b41b2315996fc654e8be4"
PROXY_ENABLED = True
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

