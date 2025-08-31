import random
from datetime import datetime
from colorama import Fore, Style
from pymongo import MongoClient
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------
# MongoDB setup using environment variables
# -------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://host.docker.internal:27017")
MONGO_DB = os.getenv("MONGO_DB", "profiles_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "profiles")
DUPLICATES_COLLECTION = os.getenv("DUPLICATES_COLLECTION", "profiles_duplicates")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
profiles = db[MONGO_COLLECTION]
duplicates = db[DUPLICATES_COLLECTION]

def iso_now():
    """Return current UTC time as YYYY-MM-DD HH:MM:SS"""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def normalize_phone(phone: str) -> str:
    """Normalize phone number consistently."""
    if not phone:
        return ""
    phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone.startswith("+1"):
        phone = phone[2:]
    if len(phone) == 11 and phone.startswith("1"):
        phone = phone[1:]
    return phone

class CleanupPipeline:
    counter = 0  # Tracks processed profiles

    def process_item(self, item, spider):
        CleanupPipeline.counter += 1
        profile_number = CleanupPipeline.counter

        # Normalize phone and name
        phone = normalize_phone(item.get("phone", ""))
        item["phone"] = phone
        name = item.get("name", "").strip()
        name_upper = name.upper() if name else ""

        # Check if phone exists in main collection
        existing = profiles.find_one({"phone": phone}) if phone else None

        if existing:
            existing_profile_id = existing.get("profile_id") or str(random.randint(10000, 99999))
            profiles.update_one({"_id": existing["_id"]}, {"$set": {"profile_id": existing_profile_id}})
            existing_name = existing.get("name", "").strip().upper()

            # Duplicate scenario: same phone, different name
            if name_upper and existing_name != name_upper:
                item.update({
                    "profile_id": existing_profile_id,
                    "created_at": existing.get("created_at", iso_now()),
                    "updated_at": iso_now(),
                    "flag": "Duplicate Phone found",
                    "flag_profile_id": existing_profile_id
                })
                duplicates.insert_one(item)
                logger.info(f"[DUPLICATE] Profile #{profile_number} flagged: {existing_profile_id}")
                print(
                    Fore.CYAN + f"\n=============== Processed Profile : {profile_number} ===============\n"
                    + Fore.YELLOW + f"=========== Existing Profile Id = {existing_profile_id} ========\n"
                    + Fore.MAGENTA + f"Flag: {item['flag']}, Flag Profile Id: {item['flag_profile_id']}\n"
                    + Fore.GREEN + f"Created At: {item['created_at']}, Updated At: {item['updated_at']}\n"
                    + Style.RESET_ALL
                )
            else:
                # Update existing profile
                update_fields = {k: v for k, v in item.items() if k in ["name", "specialities", "source_name", "url"] and v}
                if phone:
                    update_fields["phone"] = phone
                if update_fields:
                    update_fields["updated_at"] = iso_now()
                    profiles.update_one({"_id": existing["_id"]}, {"$set": update_fields})
                logger.info(f"[UPDATE] Profile #{profile_number} updated: {existing_profile_id}")
                print(
                    Fore.CYAN + f"\n=============== Processed Profile : {profile_number} ===============\n"
                    + Fore.YELLOW + f"=========== Updated Existing Profile Id = {existing_profile_id} ========\n"
                    + Style.RESET_ALL
                )
        else:
            # Insert new profile
            profile_id = str(random.randint(10000, 99999))
            item.update({
                "profile_id": profile_id,
                "created_at": iso_now(),
                "updated_at": None,
                "flag": None,
                "flag_profile_id": None
            })
            profiles.insert_one(item)
            logger.info(f"[NEW] Profile #{profile_number} inserted: {profile_id}")
            print(
                Fore.CYAN + f"\n=============== Processed Profile : {profile_number} ===============\n"
                + Fore.GREEN + f"=========== New Profile Id = {profile_id} ========\n"
                + Fore.YELLOW + f"Created At: {item['created_at']}\n"
                + Style.RESET_ALL
            )

        return item
