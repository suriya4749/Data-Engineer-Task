import random
from datetime import datetime
from colorama import Fore, Style
from pymongo import MongoClient

# Mongo setup
client = MongoClient("mongodb://mongo:27017")
db = client["profiles_db"]

profiles = db["profiles"]
duplicates = db["profiles_duplicates"]

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
            # Ensure profile_id exists in the existing document
            if "profile_id" not in existing or not existing["profile_id"]:
                existing_profile_id = str(random.randint(10000, 99999))
                profiles.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"profile_id": existing_profile_id}}
                )
                existing["profile_id"] = existing_profile_id
            else:
                existing_profile_id = existing["profile_id"]

            existing_name = existing.get("name", "").strip().upper()

            # Scenario: same phone, different name → duplicate
            if name_upper and existing_name != name_upper:
                item["profile_id"] = existing_profile_id
                item["created_at"] = existing.get("created_at", iso_now())
                item["updated_at"] = iso_now()
                item["flag"] = "Duplicate Phone found"
                item["flag_profile_id"] = existing_profile_id

                duplicates.insert_one(item)

                print(
                    Fore.CYAN + f"\n=============== Processed Profile : {profile_number} ===============\n"
                    + Fore.YELLOW + f"=========== Existing Profile Id = {existing_profile_id} ========\n"
                    + Fore.MAGENTA + f"Flag: {item['flag']}, Flag Profile Id: {item['flag_profile_id']}\n"
                    + Fore.GREEN + f"Created At: {item['created_at']}, Updated At: {item['updated_at']}\n"
                    + Style.RESET_ALL
                )

            else:
                # Same phone & same name → update existing profile
                update_fields = {}
                for key in ["name", "specialities", "source_name", "url"]:
                    val = item.get(key)
                    if val:
                        update_fields[key] = val
                # Only update phone if new value exists
                if phone:
                    update_fields["phone"] = phone

                if update_fields:
                    update_fields["updated_at"] = iso_now()
                    profiles.update_one({"_id": existing["_id"]}, {"$set": update_fields})

                print(
                    Fore.CYAN + f"\n=============== Processed Profile : {profile_number} ===============\n"
                    + Fore.YELLOW + f"=========== Updated Existing Profile Id = {existing_profile_id} ========\n"
                    + Style.RESET_ALL
                )

        else:
            # New profile → insert into main collection
            profile_id = str(random.randint(10000, 99999))
            item["profile_id"] = profile_id
            item["created_at"] = iso_now()
            item["updated_at"] = None
            item["flag"] = None
            item["flag_profile_id"] = None

            profiles.insert_one(item)

            print(
                Fore.CYAN + f"\n=============== Processed Profile : {profile_number} ===============\n"
                + Fore.GREEN + f"=========== New Profile Id = {profile_id} ========\n"
                + Fore.YELLOW + f"Created At: {item['created_at']}\n"
                + Style.RESET_ALL
            )

        return item
