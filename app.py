from flask import Flask, render_template, url_for, request
from stock_finder import *

WEBDRIVER_PATH = '/home/ilandovprais/Downloads/chromedriver'
webdriver = webdriver.Chrome(executable_path=WEBDRIVER_PATH)

finviz_scraper = finviz_page_scraper(finviz_page_finder(webdriver))
crunchbase_scraper = crunchbase_page_scraper(crunchbase_page_finder(webdriver))

app = Flask(__name__)

current_topic = ''
current_amount = 0
stocks = []
current_index = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/topic_selection')
def first():
    global current_topic
    current_topic = ''
    
    global current_amount
    current_amount = 0

    global stocks
    stocks = []

    global current_index
    current_index = 0

    return render_template('first_q.html')

@app.route('/topic_selection/<topic>')
def get_topic(topic):
    global current_topic
    current_topic = topic
    return render_template('first_q.html')

@app.route('/amount_selection')
def second():
    return render_template('second_q.html')

@app.route('/amount_selection/<amount>')
def get_amount(amount):
    global current_amount
    current_amount = amount

    return render_template('second_q.html')

@app.route('/investments_options/')
def third():
    global current_index
    print(current_index)

    if current_index == 0:
        global stocks
        stocks = finviz_scraper.scrape_page(sector=current_topic, max_price=current_amount, num_stocks=5)

    stock_json = stocks[current_index]

    another_data = crunchbase_scraper.scrape_page(stock_json['company'])

    if current_index == 0:
        current_index = current_index + 1
    else:
        current_index = (current_index + 1) % 5

    return render_template('results.html',
    url=another_data['image'],
    description=another_data['about'],
    company_name=stock_json['company'],
    country=stock_json['country'],
    industry=stock_json['industry'],
    price=stock_json['price'],
    growth=stock_json['change'])

app.run(debug=True, port=8080)