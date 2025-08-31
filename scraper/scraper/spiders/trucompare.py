import scrapy
import csv
import io
from urllib.parse import urljoin
from ..items import IdentityItem

class trucompareSpider(scrapy.Spider):
    name = "trucompare"

    custom_settings = {
        "PROXY_ENABLED":False
    }

    allowed_domains = ["trucompare.in"]
    start_urls = ["https://trucompare.in/terminsurance/assets/upload/visitor/term/"]

    def parse(self, response):
        # Extract all CSV links
        csv_links = response.css("a::attr(href)").getall()
        csv_links = [link for link in csv_links if link.lower().endswith(".csv")]

        if not csv_links:
            self.logger.error("No CSV files found.")
            return

        # Crawl all CSVs
        # for link in csv_links:
        #     file_url = urljoin(response.url, link)
        #     yield scrapy.Request(file_url, callback=self.parse_csv)
        if csv_links:
            file_url = urljoin(response.url, csv_links[0])  # only first CSV
            yield scrapy.Request(file_url, callback=self.parse_csv)

    def parse_csv(self, response):
        csv_text = response.text
        reader = csv.reader(io.StringIO(csv_text))

        for row in reader:
            if len(row) < 4:
                continue

            item = IdentityItem()

            # Name
            try:
                item["name"] = row[0].strip()
            except:
                item["name"] = None

            # DOB
            try:
                item["dob"] = row[1].strip()
            except:
                item["dob"] = None

            # Email
            try:
                item["email"] = row[2].strip()
            except:
                item["email"] = None

            # Phone
            try:
                phone_val = row[3].strip()
                phone_val = phone_val
                item["phone"] = phone_val
            except:
                item["phone"] = None

            item["source_name"] = 'trucompare.in'

            item['url'] = response.url

            yield item
