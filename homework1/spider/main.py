import bs4
import requests_html
import asyncio

async def main():

    s = requests_html.AsyncHTMLSession()

    SINA_URL = 'https://news.sina.com.cn/roll/'

    r = await s.get(SINA_URL)
    await r.html.arender()
    print(r.html.encoding)
    f = open("./tmp.html", "w", encoding=r.html.encoding)
    f.write(r.html.html)
    f.close()
    print(r.url, r.is_redirect)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())