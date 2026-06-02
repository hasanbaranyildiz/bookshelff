from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('feed/', views.feed, name='feed'),
    path('book/<int:pk>/like/', views.like_book, name='like_book'),
    path('book/<int:pk>/comment/', views.add_comment, name='add_comment'),
]