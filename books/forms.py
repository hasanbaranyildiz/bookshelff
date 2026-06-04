from django import forms
from .models import Book, Category
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Şifre sıfırlama işlemleri için gereklidir.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kullanımda. Lütfen başka bir e-posta adresi deneyin.")
        return email


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