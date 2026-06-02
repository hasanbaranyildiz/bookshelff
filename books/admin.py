from django.contrib import admin
from .models import Book, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Kategori admin paneli"""
    list_display = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Kitap admin paneli"""
    list_display = ['title', 'author', 'category', 'status', 'owner']
    list_filter = ['status', 'category']
    search_fields = ['title', 'author']