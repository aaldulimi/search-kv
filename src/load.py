from src.document import Document
from lxml import etree


def load(file_location):
    with open(file_location, 'rb') as file:
        article_count = 1
        for _, doc in etree.iterparse(file, events=('end',), tag='doc'):
            title = doc.findtext('./title')
            author = doc.findtext('./author')
            body = doc.findtext('./body')
            datetime = doc.findtext('./datetime')
            url = doc.findtext('./url')
            
            yield Document(id=article_count, title=title, author=author, body=body, datetime=datetime, url=url)
            article_count += 1
            doc.clear()