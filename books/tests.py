from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Book, Category, Like, Comment

class BookShelfTests(TestCase):
    def setUp(self):
        # Test kullanıcısı oluşturuluyor
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.client = Client()
        
        # Kategori oluşturuluyor
        self.category = Category.objects.create(name='Roman')
        
        # Örnek kitap oluşturuluyor
        self.book = Book.objects.create(
            title='Test Kitabı',
            author='Test Yazar',
            description='Test Açıklaması',
            category=self.category,
            owner=self.user,
            status='okundu'
        )

    def test_feed_page_access_and_content(self):
        """Sosyal akış (Keşfet) sayfasının erişilebilirliği ve içeriği test ediliyor."""
        # Giriş yapmamış kullanıcı logine yönlendirilmeli (302)
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 302)
        
        # Giriş yapmış kullanıcı sayfayı görebilmeli (200)
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Kitabı')

    def test_book_creation(self):
        """Kullanıcının yeni kitap ekleyebilmesi test ediliyor."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(reverse('book_create'), {
            'title': 'Yeni Eklenen Kitap',
            'author': 'Yeni Yazar',
            'status': 'okunacak',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302) # Başarılı eklemede redirect atar
        self.assertEqual(Book.objects.count(), 2)

    def test_like_system(self):
        """Kitap beğenme ve beğeniyi geri alma sistemi test ediliyor."""
        self.client.login(username='testuser', password='testpassword123')
        
        # Kitabı beğen
        self.client.get(reverse('like_book', args=[self.book.pk]), HTTP_REFERER='/feed/')
        self.assertEqual(Like.objects.count(), 1)
        
        # Kitabı beğenmekten vazgeç (aynı URL'e tekrar istek)
        self.client.get(reverse('like_book', args=[self.book.pk]), HTTP_REFERER='/feed/')
        self.assertEqual(Like.objects.count(), 0)
        
    def test_comment_and_recommendation_system(self):
        """Yorum yapma ve 'Öneriyorum' yüzdesini etkileyen sistem test ediliyor."""
        self.client.login(username='testuser', password='testpassword123')
        
        # Kitabı önererek yorum yap
        response = self.client.post(reverse('add_comment', args=[self.book.pk]), {
            'content': 'Harika bir kitap!',
            'is_recommended': 'yes'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertTrue(comment.is_recommended)
        self.assertEqual(comment.content, 'Harika bir kitap!')
