from django.db import models 
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse



class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    feeds=models.CharField(default='https://feeds.bbci.co.uk/news/rss.xml')
    keywords = models.TextField(null=True)  # comma-separated for now
    slug=models.SlugField(max_length=300, unique=True, blank=True)

    def keyword_list(self):
        return [k.strip().lower() for k in self.keywords.split(",")]
    def feeds_list(self):
        return[ feed.strip() for feed in self.feeds.split(',')if feed.strip()]
    def __str__(self):
            return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Topic.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

class RawArticle(models.Model):
    topic= models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField() 
    url = models.URLField(max_length=1000, unique=True) 
    content_raw = models.TextField() 
    author=models.TextField(max_length=250) 
    hash = models.CharField(max_length=64, unique=True)
    published_at = models.DateTimeField(null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=500, null=True)



    def __str__(self):
        return self.title






class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)

    def __str__(self):
        return self.user.username


class BlogPost(models.Model): 
    raw_article = models.ForeignKey(RawArticle, on_delete=models.CASCADE) 
    title = models.TextField() 
    content_html = models.TextField() 
    status = models.CharField(max_length=20, default="draft") 
    slug=models.SlugField(max_length=300, unique=True) 
    generated_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="edited_posts"
    )
    topic= models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)

    illustration = models.ImageField(upload_to="posts/",
                                     blank=True, 
                                     null=True,
                                     default='core/default.jpg')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('core:post_detail', args=[self.slug])

    

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