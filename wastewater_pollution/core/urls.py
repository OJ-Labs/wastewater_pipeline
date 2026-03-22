from django.urls import path
from . import views



app_name = 'core'

urlpatterns=[path('', views.home, name='home'),
             path('topics/<slug:slug>/', views.posts_by_topic, name='posts_by_topic'),
             path('post/<slug:slug>/', views.post_detail, name='post_detail'),
             ]