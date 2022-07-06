from pkgutil import iter_modules
import scrapy
import re
import json


class NaturitasSpider(scrapy.Spider):
    name = 'naturitas'
    allowed_domains = ['naturitas.es']
    start_urls = ['https://www.naturitas.es/c/u', 'https://www.naturitas.es/c/suplementos']

    def parse(self, response):
        product_links = response.css('a.product-item-link::attr(href)').extract()

        for product_link in product_links:
            yield scrapy.Request(product_link, callback=self.parse_product)
        load_more = response.css('a#load-more-product-link::attr(href)').extract_first()
        if load_more:
            original_url = response.meta.get('original_url', response.url)
            page_number = response.meta.get('page_number', 1)
            page_number += 1
            url = original_url+ f'?&p={page_number}'
            yield scrapy.Request(url, callback=self.parse, meta={'page_number': page_number, 'original_url': original_url})
    
    def parse_product(self, response):

        try:
            product_name = response.css('h1 span::text').extract_first()
            breadcrumbs_list = response.xpath("//div[contains(@class,'breadcrumbs')]/ul/li/a/text()").extract()
            breadcrumb_dict = {x:y for x,y in enumerate(breadcrumbs_list[1:])}
            images = response.xpath("//div[contains(@data-gallery-role,'gallery')]/img/@src").extract()
            product_description = response.xpath("//div[contains(@id,'product-rich-descriptive-content')]//text()").extract()
            data_dict = re.findall('"data": (\[{.*\]),', response.text)
            if data_dict:
                data = json.loads(data_dict[0])
                images = [d.get('img') for d in data]
            product_link = response.url
            product_brand = response.css('div.product-brand a::text').extract_first().strip() if response.css('div.product-brand a::text').extract_first() else ''
            product_format = response.css('div.product__presentation::text').extract_first().strip()
            reviews = response.css('div.product-reviews-summary-rating::attr(title)').extract_first()
            product_summary = response.css('a.product-reviews-summary-link::text').extract_first().strip() if response.css('a.product-reviews-summary-link::text').extract_first() else ''
            discounted_price = response.xpath("//span[@class='special-price']/span/span/span/text()").extract_first().replace('\xa0','') if response.xpath("//span[@class='special-price']/span/span/span/text()").extract_first() else ''
            normal_price = response.xpath("//span[@class='old-price msrp-price']/span/span/span/text()").extract_first().replace('\xa0','') if response.xpath("//span[@class='old-price msrp-price']/span/span/span/text()").extract_first() else ''
            sku = response.xpath("//div[@class='product__sku']/text()").extract_first().replace('SKU:','').strip() if response.xpath("//div[@class='product__sku']/text()").extract_first() else ''
            ref = response.xpath("//div[@class='product__erp-code']/text()").extract_first().strip() if response.xpath("//div[@class='product__erp-code']/text()").extract_first() else ''
            healh_claim = response.xpath("//div[@class='product-table-item-text']/a/text()").extract()
            health_claims = [x.replace(' ,  ','').strip() for x in healh_claim]
            healh_claim_dict = {f'Health claim {x+1}':value.replace(' ,  ','').strip() for x,value in enumerate(healh_claim)}
            image_dict = {f'Product image url {x+1}':y for x,y in enumerate(images)}
            item = dict()
            item['Category'] = breadcrumb_dict.get(0)
            item['Subcategory'] = breadcrumb_dict.get(1)
            item['Subcategory2'] = breadcrumb_dict.get(2,'')
            item['Brand Name'] = product_brand
            item['Product URL'] = product_link
            item['Product Name'] = product_name
            item['Format'] = product_format
            item['Description'] = ' '.join(product_description)
            item['Reviews'] = reviews
            item['Review qty'] = product_summary
            item['SKU'] = sku
            item['Ref'] = ref
            item['Discounted price'] = discounted_price
            item['Normal price'] = normal_price
            item['Images'] = ','.join(images)
            item['Health cliam'] = ','.join(health_claims)
            #item.update(image_dict)
            #item.update(healh_claim_dict)
            yield item
        except Exception as e:
            print(e)
            breakpoint() 