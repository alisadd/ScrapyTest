# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request
from datetime import datetime
import re

class VersaceSpider(Spider):
    name = 'versace'
    allowed_domains = ['versace.com']
    start_urls = ['https://www.versace.com/']
    custom_settings = {'REDIRECT_ENABLED': False}
#    handle_httpstatus_list = [302]
    
    def parse(self, response):
        '''
        Start crawler, define product categories & search for regional urls
        '''
        self.region_code = 'us/en-us'
        women_category = response.xpath('//li[a/@data-link_description="Women"]//li[@class="level-2-item js-expand-menu "]//a[@class="level-3-link category-link"]')
        for item in women_category:
            women_category_title = item.xpath('text()').extract_first().strip()
            women_category_url = item.xpath('@href').extract_first()
            women_category_url = response.urljoin(women_category_url)
            category_url = women_category_url.replace("international/en", self.region_code)
            yield Request(category_url, callback = self.parse_categories)


    def parse_categories(self, response):
        '''
        Find the number of all products in the category
        '''
        number_on_page = response.xpath('//span[@class="js-results-found-breadcrumb results-found-breadcrumb"]/text()').extract_first()
        number_on_page = re.findall(r'\d+', number_on_page)[0]
        simple_page = response.request.url + f'?start=1&sz={number_on_page}&format=page-element' 
        yield Request(simple_page, callback = self.parse_product_url)

    def parse_product_url(self, response):
        '''
        Find links to the product pages
        '''
        product_page = response.xpath('//a[@class="name-link"]/@href').extract()
        for url in product_page:
            product_url = response.urljoin(url)
            yield Request(product_url, callback = self.product_details)


    def product_details(self, response):
        '''
        Extract the data from the product pages
        '''
        product_name = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
        price = response.xpath('//span[@class="js-sl-price"]/text()').extract_first().strip()
        currency = response.xpath('//div[@itemprop="priceCurrency"]/@content').extract_first()
        color = response.xpath('//ul[@class="product-variations-list menu baseline-medium"]//a[contains(@class,"swatchanchor")]/@title').extract()
        size_block = response.xpath('//span[@class="js-swatch-value swatch-value"]/text()').extract()
        sizes = []
        for item in size_block:
            sizes.append(item.strip())
        if sizes == []:
            sizes = 'one-size'
        description_block = response.xpath('//div[@class="product-description"]//*[string-length(text()) > 5]')
        if description_block == []:
            description_block = response.xpath('//div[@class="product-description"]')
        description = description_block.xpath('.//text()').extract_first().strip()
        url = response.request.url
        time = datetime.now()
        region = self.region_code[:2]
        category = url.split('/')[5:8] 

        return {"product name": product_name,
                "color": color,
                "description": description,
                "url": url,
                "time": time,
                "price": price,
                "currency": currency,
                "size": sizes,
                "region": region,
                "category": category} 



            

