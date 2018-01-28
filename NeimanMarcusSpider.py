import scrapy
import re
import json

class NeimanMarcusSpider(scrapy.Spider):
	name = "NeimanMarcus"
	def start_requests(self):
		start_urls=['http://www.neimanmarcus.com/All-Apparel/cat58290731_cat17740747_cat000001/c.cat#userConstrainedResults=true&refinements=&page=1&pageSize=30&sort=PCS_SORT&definitionPath=/nm/commerce/pagedef_rwd/template/EndecaDrivenHome&locationInput=&radiusInput=100&onlineOnly=&updateFilter=false&allStoresInput=false&rwd=true&catalogId=cat58290731&selectedRecentSize=&activeFavoriteSizesCount=0&activeInteraction=true'];

		try:
			for url in start_urls:
				yield scrapy.Request(url=url, callback=self.parse)
		except:
			print(url)

	def parse(self, response):
		print "hereamI"
		product_urls=response.css('div.product-image-frame').xpath('@pcsclickparams').extract()
		for product in product_urls:
			yield scrapy.Request(url=product, callback=self.parse_product)

	def parse_product(self, response):
		# print response.css('title::text').extract_first()
		# print ''.join(response.css('.product-details-info.elim-suites').xpath('.//li/text()').extract())

		# prod_details=response.xpath('//script[contains(., "product_price")]/text()')
		# print 'xxxxxxxxxxxxx' 
		# print prod_details 
		# print 'xxxxxxxxxxxxxxxxxx'

		# price_pattern = re.compile(r"product_price\":?\{([^}]*)", re.MULTILINE | re.DOTALL)
		# price_dicts=json.loads('{'+prod_details.re(price_pattern)[0]+'}')

		# print '......' 
		# print prod_details 
		# print prod_details.re(price_pattern)
		# print '........'
		# print response.css('.lbl_ItemPriceSingleItem.product-price::text').extract()
		# print response.css('.lbl_ItemPriceSingleItem.product-price::text').extract_first()
		# print response.css('.lbl_ItemPriceSingleItem.product-price::text').extract_first()[0]
		# print response.css('.lbl_ItemPriceSingleItem.product-price::text').extract_first()[0].encode('ascii','ignore').split('\t').split('\n')

		# print response.css('li.color-picker').xpath('@data-color-name').extract()

		yield {
		'name':response.css('title::text').extract_first(),
		# 'img_urls':response.xpath("//meta[@property='og:image']/@content")[0].extract(),
		'image_urls': [i for i in response.css('.product-thumbnail').xpath("@src").extract()],
		'description':''.join(response.css('.productCutline').xpath('.//li/text()').extract()),
		'details': [i for i in response.css('.product-details-info.elim-suites').xpath('.//li/text()').extract()],
		'url':response.url,
		'price':response.css('.lbl_ItemPriceSingleItem.product-price::text').extract_first(),
		'color':response.css('li.color-picker').xpath('@data-color-name').extract(),
		'gender':'women'
		}
