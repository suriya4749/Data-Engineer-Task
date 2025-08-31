import re
import whois
from datetime import datetime
from urllib.parse import urlparse
from googlesearch import search
from scrapy import Item


class ScoringPipeline:

    def process_item(self, item: Item, spider):
        source_name = item.get("source_name", "")
        domain = self._extract_domain(source_name)

        # Calculate scores
        google_score = self._estimate_domain_trust(domain)
        age_score = self._get_domain_age_score(domain)
        completeness_score = self._get_data_completeness(item)

        # Final weighted trust score
        trust_score = round(
            (google_score * 0.4) +
            (age_score * 0.2) +
            (completeness_score * 0.4),
            2
        )

        item["trust_score"] = trust_score

        # Logging the breakdown
        print("\n=============== Trust Score Calculation ===============")
        print(f"Domain: {domain}")
        print(f" Google Reputation Score   : {google_score}")
        print(f" Domain Age Score          : {age_score}")
        print(f" Data Completeness Score   : {completeness_score}")
        print(f" >>> Final Trust Score     : {trust_score}")
        print("=======================================================\n")

        return item

    def _extract_domain(self, source_name: str) -> str:
        """Extract domain name (remove www, keep only hostname)."""
        if not source_name:
            return "unknown.com"
        if not source_name.startswith("http"):
            source_name = "http://" + source_name
        domain = urlparse(source_name).netloc
        domain = domain.replace("www.", "")
        return domain

    def _estimate_domain_trust(self, domain: str) -> int:
        """Estimate trust using free Google search signals."""
        query = f"site:{domain}"
        results = []
        try:
            for url in search(query, num_results=5):
                results.append(url)
        except Exception:
            return 50  # default mid trust if search fails

        trust = 30  # base score
        for url in results:
            if "wikipedia.org" in url or ".gov" in url or ".edu" in url:
                trust += 30
            elif "news" in url or "forbes" in url or "nytimes" in url:
                trust += 20
            elif "facebook.com" in url or "linkedin.com" in url:
                trust += 10
            elif "blogspot.com" in url or "wordpress.com" in url:
                trust -= 10

        return max(0, min(100, trust))

    def _get_domain_age_score(self, domain: str) -> int:
        """Score based on domain age using WHOIS."""
        try:
            w = whois.whois(domain)
            if not w.creation_date:
                return 30
            if isinstance(w.creation_date, list):
                creation_date = w.creation_date[0]
            else:
                creation_date = w.creation_date
            age_years = (datetime.now() - creation_date).days / 365
            if age_years > 10:
                return 40
            elif age_years > 5:
                return 30
            elif age_years > 1:
                return 20
            else:
                return 10
        except Exception:
            return 20

    def _get_data_completeness(self, item: Item) -> int:
        """
        Calculate completeness automatically based on the fields that have been populated
        in the current item from the spider.
        """
        if not item:
            return 0

        # Only consider fields that exist and are not None
        populated_fields = [key for key in item.keys() if key in item and item[key] is not None]

        if not populated_fields:
            return 0

        # Count fields that are non-empty / truthy
        filled_fields = sum(1 for key in populated_fields if item.get(key))
        completeness_pct = (filled_fields / len(populated_fields)) * 100

        return int(completeness_pct)
