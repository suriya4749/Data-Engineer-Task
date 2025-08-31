import datetime
import random
from pymongo import MongoClient
from neo4j import GraphDatabase

class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection, duplicates_collection,
                 neo4j_uri, neo4j_user, neo4j_password):
        # Mongo settings
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.duplicates_collection = duplicates_collection

        # Neo4j settings
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI", "mongodb://mongo:27017"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "profiles_db"),
            mongo_collection=crawler.settings.get("MONGO_COLLECTION", "profiles"),
            duplicates_collection=crawler.settings.get("DUPLICATES_COLLECTION", "profiles_duplicates"),
            neo4j_uri=crawler.settings.get("NEO4J_URI", "bolt://neo4j:7687"),
            neo4j_user=crawler.settings.get("NEO4J_USER", "neo4j"),
            neo4j_password=crawler.settings.get("NEO4J_PASSWORD", "newpassword"),
        )

    def open_spider(self, spider):
        # Mongo connection
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.profiles = self.db[self.mongo_collection]
        self.duplicates = self.db[self.duplicates_collection]

        # Neo4j connection
        self.driver = GraphDatabase.driver(
            self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
        )

    def close_spider(self, spider):
        self.client.close()
        self.driver.close()

    def normalize_phone(self, phone):
        if not phone:
            return ""
        phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if phone.startswith("+1"):
            phone = phone[2:]
        if len(phone) == 11 and phone.startswith("1"):
            phone = phone[1:]
        return phone

    def process_item(self, item, spider):
        # Normalize phone
        phone = self.normalize_phone(item.get("phone", ""))
        item["phone"] = phone
        name = item.get("name", "").strip().upper()

        # ====================
        # ✅ MongoDB Logic
        # ====================
        existing = self.profiles.find_one({"phone": phone}) if phone else None
        if existing:
            if "profile_id" not in existing or not existing["profile_id"]:
                existing_profile_id = str(random.randint(10000, 99999))
                self.profiles.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"profile_id": existing_profile_id}}
                )
                existing["profile_id"] = existing_profile_id
            else:
                existing_profile_id = existing["profile_id"]

            existing_name = existing.get("name", "").strip().upper()

            if name and existing_name != name:
                item["profile_id"] = existing_profile_id
                item["created_at"] = existing.get("created_at", datetime.datetime.utcnow())
                item["updated_at"] = datetime.datetime.utcnow()
                item["flag"] = "Duplicate Phone found"
                item["flag_profile_id"] = existing_profile_id
                self.duplicates.insert_one(item)
            else:
                update_fields = {}
                for key in ["name", "specialities", "source_name", "url"]:
                    val = item.get(key)
                    if val:
                        update_fields[key] = val
                if phone:
                    update_fields["phone"] = phone
                if update_fields:
                    update_fields["updated_at"] = datetime.datetime.utcnow()
                    self.profiles.update_one({"_id": existing["_id"]}, {"$set": update_fields})
        else:
            profile_id = str(random.randint(10000, 99999))
            item["profile_id"] = profile_id
            item["created_at"] = datetime.datetime.utcnow()
            item["updated_at"] = None
            item["flag"] = None
            item["flag_profile_id"] = None
            self.profiles.insert_one(item)

        # ====================
        # ✅ Neo4j Logic
        # ====================
        with self.driver.session() as session:
            session.write_transaction(
                lambda tx: tx.run(
                    """
                    MERGE (p:Profile {phone: $phone})
                    SET p.name = $name,
                        p.profile_id = $profile_id,
                        p.specialities = $specialities,
                        p.source_name = $source_name,
                        p.url = $url,
                        p.updated_at = datetime()
                    """,
                    phone=phone,
                    name=item.get("name"),
                    profile_id=item.get("profile_id"),
                    specialities=item.get("specialities"),
                    source_name=item.get("source_name"),
                    url=item.get("url"),
                )
            )

        return item
