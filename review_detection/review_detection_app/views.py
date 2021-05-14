from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import URLform
import pickle
import requests
import json
from bs4 import BeautifulSoup
import sklearn
from amazon_product_review_scraper import amazon_product_review_scraper

from django.template import RequestContext

def home(request):
	return HttpResponse("Hello!") 
	
def geturl(request):
	if (request.method == "POST"):
		userform = URLform(request.POST)
		url = userform.data['url']

		product_code = getProductId(url)

		allReviews = getReviews(product_code)
		json_data = allReviews.to_json(orient ='records')
		data = json.loads(json_data)

		productinfo = getProductInfo(url)
		productinfo['productid'] = product_code
		productinfo['url'] = url

		context = {'product': productinfo, 'reviews': data}

		return render(request, 'reviews.html', context)
	
	else:
		form = URLform()
		return render(request , 'form.html', {'form': form})


def getProductInfo(url):
	# Set headers
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

	# Connect to the URL
	response = requests.get(url, headers=headers)

	# Parse HTML and save to BeautifulSoup object
	soup = BeautifulSoup(response.text, "html.parser")

	try:
		title = soup.find('span', id = 'productTitle').text.strip()
	except:
		title = "Not Found"

	try:
		rating = soup.find('span', class_ = 'a-icon-alt').text.strip()
	except:
		rating = "Not Found"

	try:
		reviews = soup.find('span', id = 'acrCustomerReviewText').text.strip()
	except:
		reviews = "Not Found"

	try:
		image = soup.find('img', id = 'landingImage')['src'].strip()
	except:
		image = "Not Found"

	try:
		price = soup.find('span', id = 'priceblock_ourprice').text.strip()
	except:
		price = "Not Found"	

	return {
		"title": title,
		"rating": rating,
		"reviews": reviews,
		"image": image,
		"price": price
	}


def getReviews(product_code):
	review_scraper = amazon_product_review_scraper(amazon_site="amazon.in", product_asin = product_code, end_page = 150)
	reviews_df = review_scraper.scrape()
	Content = reviews_df['content'].tolist()
	Rating = reviews_df['rating'].tolist()
	pickle_in = open('models/review_detection.pickle', 'rb')
	pickle_clf = pickle.load(pickle_in)
	result =pickle_clf.predict(Content)
	result=result.tolist()
	total=result.count('1')
	adj_rating=[]
	for i in range(len(Content)):
		if result[i]=='1':
			s=Rating[i].split('.')
			s1=s[0]
			adj_rating.append(int(s1))
	print("Adjusted Rating is:",sum(adj_rating)/total)

	return reviews_df

def getProductId(url):
	try:
		start = url.index('dp/') + 3
	except:
		start = url.index('product/') + 8
		
	end = url[start:].index('/') + start
	product_code = url[start:end]

	print(product_code)
	return product_code

def bad_request(request):
    response = render('404.html', context_instance=RequestContext(request))
    response.status_code = 500
    return response