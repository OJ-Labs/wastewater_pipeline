from readability import Document
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def fetch_article_data(url):
        response = requests.get(url, timeout=10)
        html = response.text

        doc = Document(html)
        clean_html = doc.summary()
        # print(clean_html)

        soup = BeautifulSoup(clean_html, "html.parser")
        text = soup.get_text(separator="\n")

        full_soup = BeautifulSoup(html, "lxml-xml")
        author = None

        author_meta = full_soup.find("meta", {"name": "author"}) \
            or full_soup.find("meta", {"property": "article:author"})

        if author_meta and author_meta.get("content"):
            author = author_meta["content"]

        publish_date = None

        date_meta = (
            full_soup.find("meta", {"property": "article:published_time"}) or
            full_soup.find("meta", {"name": "pubdate"}) or
            full_soup.find("time")
        )

        if date_meta:
            publish_date = date_meta.get("content") or date_meta.get_text()

        site = urlparse(url).netloc
        return {
            "text": text.strip(),
            "author": author if author else "-",
            "publish_date": publish_date,
            "source": site,
        }



url='https://feeds.bbci.co.uk/news/rss.xml'

print(fetch_article_data(url))