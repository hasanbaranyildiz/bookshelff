from django import forms
from .models import Book, Category


class BookForm(forms.ModelForm):
    """Kitap ekleme/düzenleme formu"""
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kitap adı'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Yazar adı'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Kitap hakkında kısa açıklama',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }