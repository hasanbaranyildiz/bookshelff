from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Book, Category, Comment, Like

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Kategori admin paneli"""
    list_display = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Kitap (Gönderi) admin paneli"""
    list_display = ['title', 'author', 'category', 'status', 'owner', 'created_at', 'delete_button']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'author', 'owner__username']

    def delete_button(self, obj):
        url = reverse('admin:books_book_delete', args=[obj.id])
        return format_html('<a style="color: red; font-weight: bold;" href="{}">Sil</a>', url)
    delete_button.short_description = 'İşlem'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Yorum admin paneli"""
    list_display = ['user', 'book', 'is_recommended', 'created_at', 'delete_button']
    list_filter = ['is_recommended', 'created_at']
    search_fields = ['content', 'user__username', 'book__title']

    def delete_button(self, obj):
        url = reverse('admin:books_comment_delete', args=[obj.id])
        return format_html('<a style="color: red; font-weight: bold;" href="{}">Sil</a>', url)
    delete_button.short_description = 'İşlem'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Beğeni admin paneli"""
    list_display = ['user', 'book', 'created_at', 'delete_button']
    list_filter = ['created_at']
    search_fields = ['user__username', 'book__title']

    def delete_button(self, obj):
        url = reverse('admin:books_like_delete', args=[obj.id])
        return format_html('<a style="color: red; font-weight: bold;" href="{}">Sil</a>', url)
    delete_button.short_description = 'İşlem'