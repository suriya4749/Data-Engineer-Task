# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class IdentityItem(scrapy.Item):
    # Basic scraped fields
    name = scrapy.Field()
    phone = scrapy.Field()
    email = scrapy.Field()
    address = scrapy.Field()
    source_name = scrapy.Field()   # domain extracted from URL
    url = scrapy.Field()
    specialities = scrapy.Field()

    # Enrichment fields
    profile_id = scrapy.Field()    # unique 5-digit ID
    created_at = scrapy.Field()    # first time profile stored
    updated_at = scrapy.Field()    # updated timestamp if existing
    trust_score = scrapy.Field()   # score added in scoring_pipeline
    _id = scrapy.Field()
    flag = scrapy.Field() 
    flag_profile_id = scrapy.Field()