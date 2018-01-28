import re
import urllib2
import urllib
import cookielib
from bs4 import BeautifulSoup
import wget
import os
import pymongo
import pprint

### setup
cj = cookielib.LWPCookieJar()  
cookie_support = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)  
urllib2.install_opener(opener)
headers = {"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#"accept-encoding":"gzip, deflate, sdch, br",
"accept-language":"en-US,en;q=0.8,zh-CN;q=0.6",
"cache-control":"max-age=0",
"referer":"https://www.google.com/",
"upgrade-insecure-requests":1,
"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
}

### mongoDB setup
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client.FashionData
products = db.Test
# post = {"author": "Mike",
#         "text": "My first blog post!",
#         "tags": ["mongodb", "python", "pymongo"]
#         }
# posts = db.posts
# post_id = posts.insert_one(post).inserted_id

# print db.collection_names(include_system_collections=False)

# pprint.pprint(posts.find_one())

# request = urllib2.Request("https://shop.nordstrom.com/",headers=headers)
# response = urllib2.urlopen(request).read()

### woman: https://shop.nordstrom.com/c/womens-new-arrivals?origin=topnav&cm_sp=Top%20Navigation-_-Women-_-Featured-New%20Arrivals
### page2: https://shop.nordstrom.com/c/womens-new-arrivals?origin=topnav&cm_sp=Top%20Navigation-_-Women-_-Featured-New%20Arrivals&offset=1&page=2&top=72
### men:   https://shop.nordstrom.com/c/mens-whats-new?origin=topnav&cm_sp=Top%20Navigation-_-Men-_-Featured-New%20Arrivals
productNum = 0
pageNum = 0

prevProduct = {}
for pageNum in range(1,86):
	request = urllib2.Request("https://shop.nordstrom.com/c/womens-new-arrivals?origin=topnav&cm_sp=Top%20Navigation-_-Women-_-Featured-New%20Arrivals&offset=1&page=" + str(pageNum) + "&top=72",headers=headers)
	response = urllib2.urlopen(request).read()


	soup = BeautifulSoup(response, 'html.parser')
	### for each product
	print "here"
	for link in soup.find_all('a'):
		product = {}
		href = link.get('href')
		if href != None and href.startswith('/s/'):

			### [product url]	"https://shop.nordstrom.com" + herf
			product["url"] = "https://shop.nordstrom.com" + href
			# print "url: https://shop.nordstrom.com" + href
			request = urllib2.Request('https://shop.nordstrom.com/' + href,headers=headers)
			response2 = urllib2.urlopen(request).read()
			soup2 = BeautifulSoup(response2, 'html.parser')


			### [item name] 	soup2.find('h1').text
			if soup2.find('h1') != None:
				product["name"] = soup2.find('h1').text
				if productNum > 0 and prevProduct["name"] == product["name"]:
					continue
			# print "name: \t" + soup2.find('h1').text

			### [price]		soup2.find('div', class_ = 'current-price').text]
			if soup2.find('div', class_ = 'current-price') != None:
				product["price"] = soup2.find('div', class_ = 'current-price').text
			# print "price: \t" + soup2.find('div', class_ = 'current-price').text

			### [product description]
			if soup2.find('p', class_ = "product-selling-statement") != None:
				product["description"] = soup2.find('p', class_ = "product-selling-statement").text
			# print "description: \t" + soup2.find('p', class_ = "product-selling-statement").text
			
			### [designer]
			data_id = soup2.find('div', class_ = "product-details").get("data-reactid")
			for link4 in soup2.find_all('span', itemprop="name"):
				if link4.get("data-reactid") > data_id:
					if link4.text != None:
						product["designer"] = link4.text
					# print "designer: \t" + link4.text

			### additional label(label) and coreesponding value(label_lists) ex. [size] [width] [color]
			ID = []
			label = []
			label_lists = []
			image_urls = []
			for link2 in soup2.find_all('div', class_ = "drop-down-main-title"):
				ID.append(link2.get('data-reactid'))
				label.append(link2.text[9:])
				# print label

			for i in range(len(ID)):
				single_label_list = []
				for link3 in soup2.find_all('div', class_ = 'option-main-text'):
					if i == len(ID)-1 and link3.get('data-reactid') > ID[i]:
						single_label_list.append(link3.text)
						# print link3.text
					elif link3.get('data-reactid') > ID[i] and link3.get('data-reactid') < ID[i+1]:
						single_label_list.append(link3.text)
						# print link3.text
				# print
				label_lists.append(single_label_list)
			# print label
			# print label_lists
			for i in range(len(label)):
				product[label[i]] = label_lists[i]

			### [image]
			# for link2 in soup2.find_all('link', itemprop = "image"):
			# 	image_urls.append(link2.get('href'))
			for link2 in soup2.find_all('img'):
				if "n.nordstrommedia.com/ImageGallery/store/product/Zoom/" in link2.get('src'): 
					image_urls.append(link2.get('src'))
					print link2.get('src')
			print
			product["image_urls"] = image_urls
			# print image_urls
			# print label_lists

			### [product details]
			if soup2.find('div', class_ = "extended-product-details hide-when-immersive") != None: 
				product["details"] = soup2.find('div', class_ = "extended-product-details hide-when-immersive").text
			# print soup2.find('div', class_ = "extended-product-details hide-when-immersive").text
			
			### save single product to database 
			# product_id = products.insert_one(product).inserted_id

			### metadata
			print pageNum, productNum
			# print product
			productNum += 1
			prevProduct = product
			# pprint.pprint(products.find_one())
			# break
		# break
