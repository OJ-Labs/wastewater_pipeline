
import re
import hashlib
import feedparser
from django.core.management.base import BaseCommand
from core.models import Topic, RawArticle
from datetime import datetime
from django.core.files.base import ContentFile
import os
import requests
from urllib.parse import urljoin
from urllib.parse import urlsplit, urlunsplit
from django.db import transaction
from functools import lru_cache
from dateutil import parser




class Command(BaseCommand):
    help = "Fetch articles by topic"

    def handle(self, *args, **kwargs):

        topics = Topic.objects.all()
        if not topics:
            print("No topics to look for")
            return
        

        for topic in topics:
            self.stdout.write(f"\nProcessing topic: {topic.name}")

            keywords = tuple(topic.keyword_list())  # must be hashable for caching
            keyword_pattern = self.get_keyword_regex(keywords)
            
            for rss_url in topic.feeds_list():

                feed = feedparser.parse(rss_url)
                if feed.bozo:
                    self.stdout.write(self.style.WARNING(
                        f"Feed error for {rss_url}: {feed.bozo_exception}"
                    ))
                    continue

                for entry in feed.entries:

                    preview = entry.title + " " + getattr(entry, "summary", "")

                    # Stage 1 – preview filter
                    if not keyword_pattern.search(preview):
                        continue
                    clean_url = self.normalize_url(entry.link)
                    url_hash = hashlib.sha256(clean_url.encode()).hexdigest()

                    if RawArticle.objects.filter(url=clean_url).exists() or \
                            RawArticle.objects.filter(hash=url_hash).exists():
                                continue
                                        
                    publish_date = None

                    article_data = self.fetch_article_data(entry.link)
                    publish_date_raw = article_data["publish_date"]
                    if publish_date_raw:
                        try:
                            publish_date = parser.parse(publish_date_raw).date()
                        except Exception:
                            pass
                    if not article_data["text"]:
                        continue

                    # Stage 2 – full content filter
                    if not keyword_pattern.search(article_data["text"]):
                        continue

                    image_file = None

                    if article_data["image"]:
                        image_file = self.download_image(article_data["image"])

                    with transaction.atomic():
                        RawArticle.objects.create(
                            topic=topic,
                            title=entry.title,
                            url=clean_url,
                            content_raw=article_data["text"],
                            author=article_data["author"],
                            publish_date=publish_date,
                            source=article_data["source"],
                            hash=url_hash,
                            image=image_file
                        )

                    self.stdout.write(
                        self.style.SUCCESS(f"Saved: {entry.title}")
                    )



    @lru_cache(maxsize=None)
    def get_keyword_regex(self, keywords_tuple):
        pattern = r"\b(" + "|".join(map(re.escape, keywords_tuple)) + r")\b"
        return re.compile(pattern, re.IGNORECASE)



    def normalize_url(self, url):
        parts = urlsplit(url)
        clean = parts._replace(query="", fragment="")
        return urlunsplit(clean)

    def download_image(self, image_url):
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(image_url, headers=headers, timeout=10, stream=True)
            response.raise_for_status()

            # Skip if content type is clearly an icon
            content_type = response.headers.get("Content-Type", "")
            if any(t in content_type for t in ["image/x-icon", "image/svg", "ico"]):
                return None

            # Skip if file is too small (likely an icon)
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) < 5000:  # < 5 KB
                return None

            # Load image to inspect dimensions
            from PIL import Image
            from io import BytesIO

            img = Image.open(BytesIO(response.content))
            width, height = img.size

            # Skip tiny images (icons, badges, etc.)
            if width < 100 or height < 100:
                return None

            # Save valid image
            file_name = image_url.split("/")[-1].split("?")[0]
            return ContentFile(response.content, name=file_name)
        except Exception as e:
            print(f"Image download failed: {e}")
        return None
    


    def fetch_article_data(self, url):
        import requests
        from bs4 import BeautifulSoup
        from readability import Document
        from urllib.parse import urlparse, urljoin

        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception:
            return {"text": "", "author": "-", "publish_date": None, "source": "", "image": None}

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        paragraphs = soup.find_all("p")
        raw_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs).strip()

        if len(raw_text) < 300:  
            try:
                doc = Document(html)
                clean_html = doc.summary()
                clean_soup = BeautifulSoup(clean_html, "html.parser")
                raw_text = clean_soup.get_text(" ", strip=True)
            except Exception:
                pass


            #extracting meta data
        author = "-"
        author_meta = (
            soup.find("meta", {"name": "author"}) or
            soup.find("meta", {"property": "article:author"})
        )
        if author_meta:
            author = author_meta.get("content", "-")

        date_meta = (
            soup.find("meta", {"property": "article:published_time"}) or
            soup.find("meta", {"name": "pubdate"}) or
            soup.find("time")
        )
        publish_date = date_meta.get("content") if date_meta else None



        #image extraction
        image_url = None
        og_image = soup.find("meta", {"property": "og:image"})
        if og_image:
            image_url = og_image.get("content")

        if not image_url:
            img = soup.find("img")
            if img:
                image_url = img.get("src") or img.get("data-src")

        if image_url:
            image_url = urljoin(url, image_url)

        site = urlparse(url).netloc




        return {
            "text": raw_text,
            "author": author,
            "publish_date": publish_date,
            "source": site,
            "image": image_url,
        }
