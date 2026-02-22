
from django.db import models

# Create your models here.
from django.contrib import admin
from .models import RawArticle, BlogPost


@admin.register(RawArticle)
class RawArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_at', 'scraped_at']
    search_fields = ['title', 'author']
    readonly_fields = ['scraped_at']
    list_filter = ['published_at']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'generated_at']
    search_fields = ['title']
    list_filter = ['status', 'generated_at']
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['generated_at']



