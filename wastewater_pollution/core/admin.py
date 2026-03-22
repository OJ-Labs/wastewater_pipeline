
from django.db import models
from django_summernote.admin import SummernoteModelAdmin
from django.contrib import admin
from .models import RawArticle, BlogPost, Topic,Profile


@admin.register(RawArticle)
class RawArticleAdmin(SummernoteModelAdmin):
    summernote_fields='__all__'
    list_display = ['title', 'author', 'published_at', 'scraped_at', 'topic']
    search_fields = ['title', 'author', 'topic']
    readonly_fields = ['scraped_at']
    list_filter = ['published_at']
    


@admin.register(BlogPost)
class BlogPostAdmin(SummernoteModelAdmin):
    summernote_fields=('content',)
    list_display = ['title', 'status', 'generated_at']
    search_fields = ['title', 'content']
    list_filter = ['status', 'generated_at']
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['generated_at']


@admin.register(Topic)
class TopicAdmin(SummernoteModelAdmin):
    list_display=['name', 'keywords', 'feeds']
    summernote_fields='__all__'



@admin.register(Profile)
class ProfileAdmin(SummernoteModelAdmin):
    list_display = ['user', 'contact_email']
