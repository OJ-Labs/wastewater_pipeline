import re
import hashlib
import feedparser
from django.core.management.base import BaseCommand
from core.models import Topic, RawArticle


class Command(BaseCommand):
    help = "Fetch articles by topic"

    def handle(self, *args, **kwargs):

        topics = Topic.objects.all()
        if not topics:
            print("No topics to look for")
            return

        for topic in topics:
            self.stdout.write(f"\nProcessing topic: {topic.name}")

            keyword_pattern = re.compile(
                r"\b(" + "|".join(map(re.escape, topic.keyword_list())) + r")\b",
                re.IGNORECASE
            )

            for rss_url in topic.feeds_list():

                feed = feedparser.parse(rss_url)

                for entry in feed.entries:

                    preview = entry.title + " " + getattr(entry, "summary", "")

                    # Stage 1 – preview filter
                    if not keyword_pattern.search(preview):
                        continue

                    url_hash = hashlib.sha256(entry.link.encode()).hexdigest()

                    if RawArticle.objects.filter(hash=url_hash).exists():
                        continue

                    content = self.fetch_article_text(entry.link)

                    if not content:
                        continue

                    # Stage 2 – full content filter
                    if not keyword_pattern.search(content):
                        continue

                    RawArticle.objects.create(
                        topic=topic,
                        title=entry.title,
                        url=entry.link,
                        content_raw=content,
                        hash=url_hash,)

                    self.stdout.write(
                        self.style.SUCCESS(f"Saved: {entry.title}")
                    )

    def fetch_article_text(self, url):
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        paragraphs = soup.find_all("p")
        return " ".join(p.get_text() for p in paragraphs).strip()