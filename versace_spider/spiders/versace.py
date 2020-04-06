# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request
from datetime import datetime
import re

class VersaceSpider(Spider):
    name = 'versace'
    allowed_domains = ['versace.com']
#    start_urls = ['https://www.versace.com/']
    start_urls = ['https://www.versace.com/fr/fr-fr/home/']
    custom_settings = {'REDIRECT_ENABLED': False}
#    handle_httpstatus_list = [302]
    
    def parse(self, response):
        '''
        Start crawler, define product categories & search for regional urls
        '''
        self.region_code = 'fr/fr-fr'
        women_category = response.xpath('//li[a/@data-link_description="Women"]//li[@class="level-2-item js-expand-menu "]//a[@class="level-3-link category-link"]')
        for item in women_category:
            women_category_url = item.xpath('@href').extract_first()
            women_category_url = response.urljoin(women_category_url)
            category_url = women_category_url.replace("international/en", self.region_code)
            yield Request(women_category_url, callback = self.parse_categories)
        men_category = response.xpath('//li[a/@data-link_description="Men"]//li[@class="level-2-item js-expand-menu "]//a[@class="level-3-link category-link"]')
        for item in men_category:
            men_category_url = item.xpath('@href').extract_first()
            men_category_url = response.urljoin(men_category_url)
            yield Request(men_category_url, callback = self.parse_categories)
        jeans_category = response.xpath('//li[a/@data-link_description="Jeans Couture"]//li[@class="level-2-item js-expand-menu "]//a[@class="level-3-link category-link"]')
        for item in jeans_category:
            jeans_category_url = item.xpath('@href').extract_first()
            jeans_category_url = response.urljoin(jeans_category_url)
            yield Request(jeans_category_url, callback = self.parse_categories)
        children_panel = response.xpath('//li[contains(@class, "children-category")]')[0]
        children_category = children_panel.xpath('.//a[@class="level-2-link category-link"]')
        for item in children_category:
            children_category_url = item.xpath('@href').extract_first()
            children_category_url = response.urljoin(children_category_url)
            yield Request(children_category_url, callback = self.parse_categories)
        home_category = response.xpath('//li[a/@data-link_description="Home Collection"]//a[@class="level-3-link category-link"]/@href').extract()
        for item in home_category:
            if item.startswith('https'):
                pass
            else:
                home_url = response.urljoin(item)
                yield Request(home_url, callback = self.parse_categories)


    def parse_categories(self, response):
        '''
        Find the number of all products in the category
        '''
        number_on_page = response.xpath('//span[@class="js-results-found-breadcrumb results-found-breadcrumb"]/text()').extract_first()
        number_on_page = re.findall(r'\d+', number_on_page)[0]
        simple_page = response.request.url + '?start=0&sz=24&format=page-element'
        yield Request(simple_page, callback = self.parse_product_url)
        if int(number_on_page) > 24:
            second_page = response.request.url + '?start=25&sz=f{number_on_page}&format=page-element'
            yield Request(second_page, callback = self.parse_product_url)

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
        try:
            price = response.xpath('//span[@class="js-sl-price"]/text()').extract_first().strip()
        except AttributeError:
            price = []
            price_range = response.xpath('//div[@class="price-range"]//span[contains(@itemprop, "Price")]/text()').extract()
            for item in price_range[:2]:
                price.append(item.strip())
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
        sku_block = response.xpath('//script[contains(text(), "window.universal_variable.product")]').extract_first() 
        sku = re.search('sku":\"(.*?)\"', sku_block).group(1)

        return {"product name": product_name,
                "color": color,
                "description": description,
                "url": url,
                "time": time,
                "price": price,
                "currency": currency,
                "size": sizes,
                "region": region,
                "category": category,
                "sku": sku} 



            

