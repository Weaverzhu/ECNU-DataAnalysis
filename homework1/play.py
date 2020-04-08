import requests_html
from bs4 import BeautifulSoup

s = requests_html.HTMLSession()

TX_NEWS_URL = "https://news.qq.com/"

print("all set")

r = s.get(TX_NEWS_URL)
r.html.render()

print(r.encoding)