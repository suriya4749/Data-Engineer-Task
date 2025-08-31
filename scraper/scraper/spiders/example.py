# import scrapy
# from scraper.items import IdentityItem

# class ExampleSpider(scrapy.Spider):
#     name = "example"
#     start_urls = ["https://quotes.toscrape.com/"]  # demo site

#     def parse(self, response):
#         for quote in response.css("div.quote"):
#             item = IdentityItem()
#             item["name"] = quote.css("span small.author::text").get()
#             item["phone"] = "123-456-7890"  # mock phone for demo
#             item["source"] = "quotes.toscrape.com"
#             item["url"] = response.url
#             yield item
