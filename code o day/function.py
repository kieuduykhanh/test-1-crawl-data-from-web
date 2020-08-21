from bs4 import BeautifulSoup
import urllib.request
from testFun import post, getComment, get
import json
import time
import csv


def crawlDataFromWeb(url):
	start = time.time()
	page = urllib.request.urlopen(url)
	soup = BeautifulSoup(page, 'html.parser')

	try:
		books = soup.find('table', class_="tableList").findAll('tr', itemtype="http://schema.org/Book")
	except:
		books = []

	sum = []
	for feed in books:
		fee1 = feed.find('a')
		fee2 = feed.find('div', class_="u-anchorTarget")
		fee3 = feed.find('a', class_="authorName")
		title = fee1.get('title')
		link = fee1.get('href')
		id = int(fee2.get('id'))
		sum.append({'title': title, 'link': 'https://www.goodreads.com'+link, 'sach_id' : id, 'author': fee3.text})

	for book in sum:
		print("Running...")
		book = xulyBook(book)

	end = time.time()

	print("time xu ly: ",(end - start))

	with open('dataWeb.txt', 'w', encoding='utf8') as outfile:
		json.dump(sum, outfile, ensure_ascii=False)

	with open('dataWeb.csv', 'w', encoding='utf-8') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(['ID Sach', 'Title', 'Link', 'Author', 'Rate', 'Description', 'Review'])
		for sach in sum:
			writer.writerow([sach['sach_id'], sach['title'], sach['link'], sach['author'], sach['rate'], sach['description'], sach['review']])

	choose = int(input('Du lieu da luu vao file data.txt va data.csv, chon 1 de luu vao database (khong luu - chon so khac): '))
	if choose == 1:
		inputToDB(sum)
		print("Da lu vao database.")


def xulyUser(user):
	if('/user/show/' in user):
		user = user.replace('/user/show/', '')
		if '-' in user:
			user = user[:user.index('-')]
	return int(user)

def xulyBook(data):
	page = urllib.request.urlopen(data['link'])
	soup = BeautifulSoup(page, 'html.parser')
	rate = soup.find('div', id='topcol').find('div',
			id='metacol').find('div', id='bookMeta').find('span', itemprop="ratingValue")
	data['rate'] = float((rate.text))
	try:
		book = soup.find('div', id="description", class_="readable stacked").find('span', style="")
		data['description'] = book.text
	except:
		data['description'] = ''
	data['review'] = []
	reviews = soup.find('div', id="bookReviews").findAll('div', class_="friendReviews elementListBrown")
	for review in reviews:
		data_review = {}
		content = review.find('div', class_="reviewText stacked").find('span',
										class_="readable").find('span', style=None)
		name = review.find('div', class_="reviewHeader uitext stacked").find('span',
																			 itemprop="author").find('a')
		date_post = review.find('div', class_="reviewHeader uitext stacked").find('a',
															  class_="reviewDate createdAt right")
		rate = review.find('div', class_="reviewHeader uitext stacked").findAll('span',
																			class_="staticStar p10")

		data_review['user_id'] = xulyUser(name.get('href'))
		data_review['name_user'] = name.get('name')
		data_review['rate'] = len(rate)
		data_review['review_content'] = content.text
		data_review['date_post'] = date_post.text
		commen = review.find('div').find('div').find('div',
		class_="left bodycol").find('div', class_="reviewFooter uitext buttons").find('div',
																				class_="updateActionLinks")
		data_review['link_review'] = 'https://www.goodreads.com' + commen.findAll('a')[-1].get('href')
		data_review['comment'] = getComment(data_review['link_review'])
		data['review'].append(data_review)
	return data


def inputToDB(arrData):
	for data in arrData:
		post(data)

def getDataFromDatabase():
	sum = get()
	with open('dataDB.txt', 'w', encoding='utf8') as outfile:
		json.dump(sum, outfile, ensure_ascii=False)

	with open('dataDB.csv', 'w', encoding='utf-8') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(['ID Sach', 'Title', 'Link', 'Author', 'Rate', 'Description', 'Review'])
		for sach in sum:
			writer.writerow([sach['sach_id'], sach['title'], sach['link'], sach['author'], sach['rate'], sach['description'], sach['review']])
