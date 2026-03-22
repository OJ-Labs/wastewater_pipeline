from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Profile, Topic, RawArticle
from django.core.paginator import Paginator



def home(request):
    featured_posts = BlogPost.objects.filter(is_featured=True)[:3]
    posts = BlogPost.objects.exclude(id__in=featured_posts).order_by('-created_at')
    paginator = Paginator(posts, 5)  # 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'core/home.html'
    return render(request, template, {
        'page_obj': page_obj,
        'featured_posts': featured_posts,
    })



def posts_by_topic(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    posts = BlogPost.objects.filter(topic=topic)

    return render(request, 'core/posts_by_topic.html', {
        'posts': posts,
        'current_topic': topic
    })



def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'core/post_detail.html',{
        'post': post
    })
