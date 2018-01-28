import scrapy
import re
import json

class NetAPorterSpider(scrapy.Spider):
	name = "net-a-porter"
	def start_requests(self):
		start_urls=['https://www.net-a-porter.com/us/en/d/Shop/Clothing/Coats?cm_sp=topnav-_-clothing-_-coats&pn=1&npp=60&image_view=product&dScroll=0'];
		try:
			for url in start_urls:
				yield scrapy.Request(url=url, callback=self.parse)
		except:
			print(url)

	def parse(self, response):
		print "here"
		product_urls=response.css('div.product-image a').xpath('@href').extract()
		print product_urls
		for product in product_urls:
			yield scrapy.Request(url='https://www.net-a-porter.com'+product, callback=self.parse_product)

	def parse_product(self, response):
		name = response.css('title::text').extract_first();
		name = name.split("|")[1].strip();
		price = response.css('meta.product-data').xpath('@data-price').extract()[0].encode('ascii')
		price = price[:-2] + '.' + price[-2:]
		yield {
		'name':name,
		'image_urls': [('https:'+i) for i in response.css('img.product-image').xpath("@src").extract()],
		'description':''.join(response.css('div.wrapper p::text').extract()).strip('\t\n'),
		'details': [i for i in response.css('ul.font-list-copy').xpath('.//li/text()').extract()],
		'url':response.url,
		'price':price,
		'color':response.css('li.color-picker').xpath('@data-color-name').extract(),
		'style':['Coats']
		}
