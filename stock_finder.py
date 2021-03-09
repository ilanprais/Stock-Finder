from selenium import webdriver
from bs4 import BeautifulSoup

class finviz_page_finder:

	URL = 'https://finviz.com/screener.ashx?v=111'

	def __init__(self, webdriver):
		self.__webdriver = webdriver

	def get_page(self, **options):
		url = f'{self.URL}&f=sec_{options["sector"]},sh_price_u{options["max_price"]}&o=-change'
		self.__webdriver.get(url)

		return self.__webdriver.page_source

class crunchbase_page_finder:

	URL = 'https://www.crunchbase.com/organization/'

	def __init__(self, webdriver):
		self.__webdriver = webdriver

	def get_page(self, company_name):
		stripped_company_name = company_name.replace(',', '')
		while stripped_company_name[-1] == '.' or stripped_company_name[-1] == ',':
			stripped_company_name = stripped_company_name[:-1]

		stripped_company_name = stripped_company_name.replace(' ', '-').replace('&', '-').lower()

		url = self.URL + stripped_company_name
		self.__webdriver.get(url)

		soup = BeautifulSoup(self.__webdriver.page_source, 'lxml')
		if soup.find('div', class_='one-of-many-section ng-star-inserted') is not None:
			return self.__webdriver.page_source

		while True:
			stripped_company_name = stripped_company_name[:max(stripped_company_name.rfind('-'), stripped_company_name.rfind('.'))]
			while stripped_company_name[-1] == '.' or stripped_company_name[-1] == ',':
				stripped_company_name = stripped_company_name[:-1]

			url = self.URL + stripped_company_name
			self.__webdriver.get(url)

			soup = BeautifulSoup(self.__webdriver.page_source, 'lxml')
			if soup.find('div', class_='one-of-many-section ng-star-inserted') is not None:
				return self.__webdriver.page_source

class finviz_page_scraper:

	def __init__(self, finviz_page_finder):
		self.__finviz_page_finder = finviz_page_finder

	def scrape_page(self, **options):
		page = self.__finviz_page_finder.get_page(sector=options['sector'], max_price=options['max_price'])
		soup = BeautifulSoup(page, 'lxml')

		stocks = []

		table = soup.find('table', attrs={'bgcolor' : '#d3d3d3'})
		table_body = table.find('tbody')

		rows = table_body.find_all('tr')
		for row in rows[1:options['num_stocks'] + 1]:
		    cols = row.find_all('td')

		    stock_json = {}
		    stock_json['url'] = 'https://finviz.com/' + cols[2].a['href']
		    stock_json['company'] = cols[2].text
		    stock_json['sector'] = cols[3].text
		    stock_json['industry'] = cols[4].text
		    stock_json['country'] = cols[5].text
		    stock_json['price'] = float(cols[8].text)
		    stock_json['change'] = float(cols[9].text[:-1])

		    stocks.append(stock_json)

		return stocks

class crunchbase_page_scraper:

	def __init__(self, crunchbase_page_finder):
		self.__crunchbase_page_finder = crunchbase_page_finder

	def scrape_page(self, company_name):
		page = self.__crunchbase_page_finder.get_page(company_name)
		soup = BeautifulSoup(page, 'lxml')

		stock_json = {}
		stock_json['image'] = soup.find_all('img')[2]['src']
		stock_json['about'] = soup.find(class_='description').text

		return stock_json

if __name__ == '__main__':
	WEBDRIVER_PATH = '/home/yonatan/Projects/chromedriver'
	webdriver = webdriver.Chrome(executable_path=WEBDRIVER_PATH)

	finviz_scraper = finviz_page_scraper(finviz_page_finder(webdriver))
	crunchbase_scraper = crunchbase_page_scraper(crunchbase_page_finder(webdriver))
	stock_json = finviz_scraper.scrape_page(sector='consumercyclical', max_price=5, num_stocks=10)
	print(stock_json)
	print(crunchbase_scraper.scrape_page(stock_json[0]['company']))