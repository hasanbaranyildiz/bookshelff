from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """Kitap kategorisi modeli"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Book(models.Model):
    """Ana kitap modeli"""
    STATUS_CHOICES = [
        ('okunacak', 'Okunacak'),
        ('okunuyor', 'Okunuyor'),
        ('okundu', 'Okundu'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='okunacak')
    views_count = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme Sayısı")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        verbose_name_plural = "Likes"

    def __str__(self):
        return f"{self.user.username} likes {self.book.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_recommended = models.BooleanField(default=True, verbose_name="Öneriyor mu?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.book.title}"