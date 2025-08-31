import scrapy,json
from ..items import IdentityItem
from ..utils.user_agents import get_fake_user_agent

class NpiregistrySpider(scrapy.Spider):

    custom_settings = {
        "PROXY_ENABLED":False
    }

    name = 'npiregistry'

    def start_requests(self):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://npiregistry.cms.hhs.gov',
            'priority': 'u=1, i',
            'referer': 'https://npiregistry.cms.hhs.gov/provider-view/1386663896',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': get_fake_user_agent()
        }
        ## Testing Mode
        single_url = getattr(self, 'single_url', None)
        if single_url and 'http' in single_url:
            print('[+] spider running in QA - single url mode [+]', single_url)
            yield scrapy.Request(single_url, headers=headers, callback=self.parse)
        else:
            print('[+] spider running Normal mode [+]')

            # Get CLI args passed via -a start=... -a end=...
            start_arg = getattr(self, 'start', None)
            end_arg = getattr(self, 'end', None)

            # Convert to integers if possible
            try:
                start = int(start_arg) if start_arg and not callable(start_arg) else None
            except ValueError:
                start = None

            try:
                end = int(end_arg) if end_arg and not callable(end_arg) else None
            except ValueError:
                end = None

            with open('scraper/npi.txt') as f:
                data = [line.strip() for line in f if line.strip()]  # strip and skip blanks
                data = data[start:end]

            for i in data:
                link = (
                    f'https://npiregistry.cms.hhs.gov/api/?number={i}'
                    f'&enumeration_type=NPI-1&taxonomy_description=&first_name=&use_first_name_alias='
                    f'&last_name=&organization_name=&address_purpose=&city=&state=&postal_code=&country_code=&limit=&skip=&version=2.1'
                )
                yield scrapy.Request(link, headers=headers, callback=self.parse, dont_filter=True)

    
    def parse(self,response):
        

        item_list = json.loads(response.text)

        values = item_list['results']

        if values and len(values) >= 1:

            for value in values:
                item = IdentityItem()
                nameChunk = value["basic"]
                try:
                    first_name = nameChunk["first_name"]
                except:
                    first_name = None
                if not first_name:
                    try:
                        first_name = nameChunk["authorized_official_first_name"]
                    except:
                        first_name = None
                try:
                    last_name = nameChunk["last_name"]
                except:
                    last_name = None
                if not last_name:
                    try:
                        last_name = nameChunk["authorized_official_last_name"]
                    except:
                        last_name = None
                try:
                    middle_name = nameChunk["middle_name"]
                except:
                    middle_name =  None
                if not middle_name:
                    try:
                        middle_name = nameChunk["authorized_official_middle_name"]
                    except:
                        middle_name = None

                if "None" not in str(first_name) and "None" not in str(middle_name) and "None" not in str(last_name):

                    item["name"] = '{} {} {}'.format(str(first_name),str(middle_name),str(last_name))

                if "None" in str(middle_name) and "None" not in str(first_name) and "None" not in str(last_name):

                    item["name"] = '{} {}'.format(str(first_name),str(last_name))
                
                if  "None" in str(last_name) and "None" not in str(first_name) and "None" not in str(middle_name):
                    
                    item["name"] = '{} {}'.format(str(first_name),str(middle_name))
                
                if  "None" in str(last_name) and "None" in str(middle_name) and "None" not in str(first_name):
                    
                    item["name"] = first_name
                
                try:
                    valChunk = value["addresses"]
                except:
                    valChunk = None

                if valChunk and len(valChunk) > 0:
                    for items in valChunk:

                        try:
                            item["phone"] = items['telephone_number'].replace('+1','')
                        except:
                            item["phone"] = None
                
                item["source_name"] = "npiregistry.cms.hhs.gov"
                item["url"] = response.url

                try:
                    specData1 =  value["taxonomies"]
                    if specData1:
                        item["specialities"] = list(set(vals['desc'] for vals in specData1))
                    else:
                        item["specialities"] = None
                except:
                    item["specialities"] = None
                
                if item["specialities"] == []:
                    item["specialities"] = None
                

                yield item