import scrapy
from scrapy.utils.response import open_in_browser
from collections import  OrderedDict

class GoogleSearch(scrapy.Spider):
    name = 'google_search'
    base_url = 'https://www.google.com'
    start_url = 'https://www.google.com/search?q='

    parent_keywords = ["parent addiction", "father addiction", "mother addiction",
                       "dad addiction", "mom addiction", "parent addict",
                       "mother addict", "father addict", "parent alcoholic",
                       "mom alcoholic", "dad alcoholic", "dad drugs",
                       "father drugs", "mom drugs", "mother drugs",
                       "child of an addict", "child of an alcoholic"]

    addictions = ["Cocaine","Crack Cocaine", "crack", "pills", "alcohol",
                  "heroin", "PAIN MEDS", "drugs", "drank",
                  "ALCOHOLIC", "prescripton pills", "diet pills",]

    person_names = ["Kevin Hart", "Mario", "Charlize Theron", "Dwayne Wade", "Cristiano Rinaldo"]
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/87.0.4280.88 Mobile Safari/537.36'
    }

    def start_requests(self):
        for name in self.person_names:
            for parent_keyword in self.parent_keywords[:]:
                yield scrapy.Request(f'{self.start_url+parent_keyword} {name}',
                                     headers=self.headers,
                                     callback=self.parse,
                                     meta={'keyword': parent_keyword, 'name': name})

    def parse(self, response):
        search_urls = response.css('a::attr(href)').getall()
        if search_urls:
            search_urls = [url for url in search_urls if ('https' in url or 'http' in url) and 'google' not in url and 'youtube' not in url]
            # pending_search_urls = search_urls[1:]
            #
            # response.meta['pending_search_urls'] = pending_search_urls

            for url in search_urls[:1]:
                yield scrapy.Request(url,
                                     headers=self.headers,
                                     callback=self.detail,
                                     meta=response.meta)

    def detail(self, response):
        item = OrderedDict()
        description = response.css('*::text').getall()
        description = ''.join(description)
        scraped_addictions = []

        for addiction in self.addictions:
            if addiction.lower() in description.lower():
                item['Name'] = response.meta['name']
                item['Addiction'] = addiction
                item['Parent'] = response.meta['keyword'].replace('addiction','')
                item['Evidence'] = response.url
                scraped_addictions.append(addiction)
                yield item
                break
