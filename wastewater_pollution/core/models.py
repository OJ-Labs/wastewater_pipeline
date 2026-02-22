from django.db import models 
from django.utils.text import slugify


class RawArticle(models.Model):
    title = models.TextField() 
    url = models.URLField(unique=True) 
    content_raw = models.TextField() 
    author=models.TextField(max_length=50) 
    hash = models.CharField(max_length=64, unique=True)
    published_at = models.DateTimeField(null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)


class BlogPost(models.Model): 
    raw_article = models.ForeignKey(RawArticle, on_delete=models.CASCADE) 
    title = models.TextField() 
    content_html = models.TextField() 
    status = models.CharField(max_length=20, default="draft") 
    slug=models.SlugField(max_length=300, unique=True) 
    generated_at = models.DateTimeField(auto_now_add=True)
    raw_article = models.OneToOneField(RawArticle, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)