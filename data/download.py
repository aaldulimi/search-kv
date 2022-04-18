import requests
from selectolax.parser import HTMLParser
import datetime
import asyncio
import aiohttp
import random
import xml.dom.minidom
import xml.etree.ElementTree as ET

headers = {
    'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.{random.randint(0, 9999)} Safari/537.{random.randint(0, 99)}'  
}

all_days = []

base_url = 'https://www.nytimes.com/sitemap/2021/'
response = requests.get(base_url, headers=headers)

with open("data/data.xml", 'w') as file:
    file.write('<documents>\n')
    file.close()

for node in HTMLParser(response.text).css('div > ol > li'):
    url = base_url + node.child.attrs['href']

    response = requests.get(url)
    for node in HTMLParser(response.text).css('div > ol > li'):
        day_url = url + node.child.attrs['href']
        all_days.append(day_url)


article_count = 0
to_load = []
async def get_article_data(session, url):
    async with session.get(url) as resp:
        response_text = await resp.text()
        
        if response_text:            
            article = HTMLParser(response_text)

            title = article.css_first('h1')
            if title == None: return 
            title = title.text()

            try:
                date = article.css_first('time')
                date = date.attributes['datetime']
                if 'Z' in date: date = date[:date.find('.000Z')] + '+00:00'
                date = datetime.datetime.fromisoformat(date)
                date = date.strftime('%Y-%m-%d %H:%M:%S')

            except:
                date = ''

            author = article.css_first('span.last-byline')
            if author == None: author = 'unkown' 
            else: author = author.child.text()

            body = ''
            for node in article.css('div.StoryBodyCompanionColumn'):
                paragraph = node.child.select('p').matches
                for p in paragraph:
                    if p: body += p.text()

            doc = ET.Element('doc')
            ET.SubElement(doc, "title").text = title
            ET.SubElement(doc, "author").text = author
            ET.SubElement(doc, "body").text = body
            ET.SubElement(doc, "datetime").text = date
            ET.SubElement(doc, "url").text = url

            dom = xml.dom.minidom.parseString(ET.tostring(doc))
            doc = dom.childNodes[0].toprettyxml()

            global to_load, article_count
            to_load.append(doc)
            
            if len(to_load) >= 10:
                with open("data/data.xml", 'a') as file:
                    for doc in to_load:
                        file.write(doc)

                    file.close()

                to_load = []
                
            article_count += 1
        return 

async def get_article_url(session, url):
    async with session.get(url) as resp:
        day_data = await resp.text()

        all_articles = []
        for node in HTMLParser(day_data).css('div > ul:nth-child(4) > li'):
            if node.child.text() == "Read the document": continue
            article_url = node.child.attrs['href']
            if article_url.find('.com/interactive') != -1 or article_url.find('books/review/') != -1: continue
            
            all_articles.append(asyncio.ensure_future(get_article_data(session, article_url)))

        collection = await asyncio.gather(*all_articles)


async def main():
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for day_url in all_days[:10]: 
            tasks.append(asyncio.ensure_future(get_article_url(session, day_url)))
        
        collection = await asyncio.gather(*tasks)


asyncio.run(main())


with open("data/data.xml", 'a') as file:
    file.write('</documents>')
    file.close()