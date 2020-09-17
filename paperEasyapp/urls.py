from django.shortcuts import redirect
from django.urls import path
from . import views
from .views import PostListView, PostDetailView

urlpatterns = [
    path('', views.home, name="home"),
    path('second', views.second),
    path('third', views.third, name='third'),
    path('post/', PostListView.as_view(), name='post_list'),
    path('detail/<int:pk>', PostDetailView.as_view(), name='post_detail'),
    path('add/', views.add),
    path('add/create', views.create, name='create'),
    path('post/edit/<int:pk>', views.update, name='update_post'),
    path('post/<int:pk>/delete', views.delete, name='delete_post'),
    path('find/', views.find),
    path('createcomment/<int:pk>', views.createcomment, name='create_comment'),
    path('createcomment/add/<int:pk>', views.createcomment),
]
