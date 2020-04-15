import bs4
import requests_html
import asyncio
import requests
import re
import datetime
import pyppeteer
import pandas as pd
import traceback

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

err_log = 'err.log'


def requests_retry_session(
    retries=10,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


SINA_URL = 'https://news.sina.com.cn/roll/'
sample_url = "https://finance.sina.com.cn/roll/2020-04-03/doc-iimxxsth3469383.shtml"

url_pattern = re.compile(
    r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$')
news_url_pattern = re.compile(
    r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+[^(copyright)]\.shtml$')


def __isValidUrl__(url: str) -> bool:
    a = url_pattern.findall(url)
    return len(a) > 0


def __isValidNewsUrl__(url: str) -> bool:
    a = news_url_pattern.findall(url)
    return len(a) > 0


class DataSource:
    def __init__(self):
        self.xpath = []

    def __init__(self, xpath):
        self.xpath = xpath

    def add(self, tag: str, attrs: dict()):
        self.xpath.append((tag, attrs))


DATE_SOURCE = [
    DataSource([('div', {'class': 'date-source'}), ('span', 'date')]),
    DataSource([('div', {'class': 'artInfo'}), ('span', {'id': 'pub_date'})])
]


def get_page_url(date: datetime.date, page_num=1) -> str:
    start = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    end = start + datetime.timedelta(days=1)

    etime = int(start.timestamp())
    stime = ctime = int(start.timestamp())

    date_str = date.strftime("%Y-%m-%d")

    return f"https://news.sina.com.cn/roll/#pageid=153&lid=2509&etime={etime}&stime={stime}&ctime={ctime}&date={date_str}&k=&num=50&page={page_num}"


async def get_news_links_from_page_url(url: str) -> list:
    # print(f"get news links: url={url}")
    if not __isValidUrl__(url):
        raise Exception(f"not valid url :|{url}|")

    s = requests_html.AsyncHTMLSession()
    try:
        r = await s.get(url)
        await r.html.arender()
        html = r.html.html.encode(r.html.encoding).decode('utf8', 'ignore')
        bs = bs4.BeautifulSoup(r.html.html, 'html.parser')
        links = bs.findAll('a')
        res = []
        for link in links:
            url = link['href']
            if __isValidUrl__(url):
                res.append(url)
        return res
    finally:
        await s.close()


class SinaNews:

    def __add_attr__(self, attr: str, tags: bs4.Tag, f=""):
        # print(f"in __add_attr__: attr={attr} tags={tags} f={f}")
        if tags is None:
            raise Exception(f'{attr} not found, url: {self.url}')
        if len(f) > 0:
            if f == 'text':
                self.__dict__[attr] = tags.get_text()
            else:
                self.__dict__[attr] = tags.attrs[f]
        else:
            self.__dict__[attr] = tags

    def __init__(self, url: str, s: requests.Session, date: datetime.datetime, bs: bs4.BeautifulSoup):
        # print(f"init {url}")
        self.url = url
        self.publish_date = date.isoformat()

        # self.main_title = bs.find('title').text
        self.__add_attr__('main_title', bs.find('title'), 'text')
        # self.keywords = bs.find(
        #     'meta', attrs={'name': 'keywords'}).content.split(',')
        self.__add_attr__('keywords', bs.find(
            'meta', attrs={'name': 'keywords'}), 'content')
        self.keywords = self.keywords.split(',')

        self.__add_attr__('xpath', bs.find(
            'div', attrs={'class': 'channel-path'}), 'text')

        self.xpath = self.xpath.split('>')

        for idx, path in enumerate(self.xpath):
            path = path.replace('\n', '')
            path = path.replace(' ', '')
            path = path.replace(u'\xa0', '')
            path = path.replace('\t', '')
            path = path.strip()
            self.xpath[idx] = path
        self.xpath = " ".join(self.xpath)


def collectNewsFromDays(start_date: datetime.date, end_date: datetime.date, max_page_num=50) -> list:
    def collectNews(date: datetime.date, max_page_num=50) -> list:
        print(f"collecting news on {date}")
        res = []
        with requests_retry_session() as session:
            for page_num in range(1, max_page_num+1):
                page_url = get_page_url(date, page_num)
                print(f"page {page_num}, page url: {page_url}")
                news_links = asyncio.run(
                    get_news_links_from_page_url(page_url))
                # print(news_links)
                for news_link in news_links:
                    if __isValidNewsUrl__(news_link):

                        r = s.get(news_link)
                        bs = bs4.BeautifulSoup(r.text.encode(
                            r.encoding).decode('utf8', 'ignore'), 'html.parser')

                        news_type = bs.find(
                            'meta', attrs={'property': 'og:type'})
                        if news_type is not None:
                            news_type = news_type['content']
                            if news_type != 'news':
                                continue

                        if news_link.find('toujiao') != -1:
                            continue
                        try:
                            publish_time = datetime.datetime.strptime(bs.find(
                                'span', attrs={'class': 'date'}).text, '%Y年%m月%d日 %H:%M')

                            res.append(
                                SinaNews(news_link, session, publish_time, bs))
                        except Exception as e:
                            with open(err_log, 'w+') as f:
                                f.write(
                                    f'err in news_link {news_link} in page_url {page_url}')
                                traceback.print_exc(limit=2, file=f)

        return res

    day_delta = datetime.timedelta(days=1)
    newsList = []
    print(start_date, end_date)
    while start_date < end_date:
        try:
            newsList += collectNews(start_date, max_page_num)
        except Exception as e:
            with open(err_log, 'w+') as f:
                f.write(f'err in date {start_date}')
                traceback.print_exc(limit=2, file=f)

        start_date = start_date + day_delta

    return newsList


def toDataFrame(news: list, sample_news: SinaNews) -> pd.DataFrame:
    d = dict()
    attrs = sample_news.__dict__.keys()
    for attr in attrs:
        d[attr] = []
    for n in news:
        for attr in attrs:

            if attr in n.__dict__.keys():
                d[attr].append(n.__dict__[attr])
            else:
                d[attr].append(None)
    df = pd.DataFrame(data=d)
    print(df.head())
    return df


sample_news_url = "https://finance.sina.com.cn/chanjing/2020-04-15/doc-iirczymi6429991.shtml"

today = datetime.date.today()

with requests_retry_session() as s:
    r = s.get(sample_news_url)
    bs = bs4.BeautifulSoup(r.text.encode(
        r.encoding).decode('utf8', 'ignore'), 'html.parser')
    sample_news = SinaNews(sample_news_url, s, today, bs)


df = toDataFrame(collectNewsFromDays(
    today - datetime.timedelta(days=14), today, max_page_num=50), sample_news)
df.to_csv(f'.news.csv')

