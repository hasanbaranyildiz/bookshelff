import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import login
from .forms import BookForm, CustomUserCreationForm
from .models import Book, Category, Like, Comment
from django.db.models import Count



@login_required
def book_list(request):
    """Kitap listesi - arama ve filtreleme"""
    books = Book.objects.filter(owner=request.user)
    query = request.GET.get('q')
    if query:
        books = books.filter(title__icontains=query)
    status = request.GET.get('status')
    if status:
        books = books.filter(status=status)
    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(category_id=category_id)
    paginator = Paginator(books, 6)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    categories = Category.objects.all()
    return render(request, 'books/book_list.html', {
        'books': books,
        'categories': categories,
    })


@login_required
def book_detail(request, pk):
    """Kitap detay sayfası"""
    book = get_object_or_404(Book, pk=pk)
    comments = book.comments.all().order_by('-created_at')
    total_comments = comments.count()
    recommended_count = comments.filter(is_recommended=True).count()
    recommendation_percentage = int((recommended_count / total_comments * 100)) if total_comments > 0 else 0
    is_liked = book.likes.filter(user=request.user).exists()
    
    return render(request, 'books/book_detail.html', {
        'book': book,
        'comments': comments,
        'recommendation_percentage': recommendation_percentage,
        'is_liked': is_liked,
    })


@login_required
def book_create(request):
    """Yeni kitap ekleme"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            messages.success(request, 'Kitap başarıyla eklendi!')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Kitap Ekle'})


@login_required
def book_update(request, pk):
    """Kitap düzenleme"""
    book = get_object_or_404(Book, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kitap güncellendi!')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Kitap Düzenle'})


@login_required
def book_delete(request, pk):
    """Kitap silme"""
    book = get_object_or_404(Book, pk=pk, owner=request.user)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Kitap silindi!')
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


def signup(request):
    """Kullanıcı kayıt sayfası"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Hesabın oluşturuldu, hoş geldin!')
            return redirect('book_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def feed(request):
    """Sosyal Akış (Keşfet) sayfası"""
    books = Book.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    ).order_by('-created_at').prefetch_related('comments', 'comments__user')
    
    user_likes = list(Like.objects.filter(user=request.user).values_list('book_id', flat=True))
    
    return render(request, 'books/feed.html', {'books': books, 'user_likes': user_likes})

@login_required
def like_book(request, pk):
    """Kitap beğenme / beğenmekten vazgeçme"""
    book = get_object_or_404(Book, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, book=book)
    if not created:
        like.delete() # Un-like if already liked
    return redirect(request.META.get('HTTP_REFERER', 'book_detail'))

@login_required
def add_comment(request, pk):
    """Yorum yapma"""
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=pk)
        content = request.POST.get('content')
        is_recommended = request.POST.get('is_recommended') == 'yes'
        if content:
            Comment.objects.create(
                user=request.user,
                book=book,
                content=content,
                is_recommended=is_recommended
            )
            messages.success(request, 'Yorumunuz eklendi.')
    return redirect('book_detail', pk=pk)

@login_required
def chatbot_api(request):
    """BookShelf Asistan API endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'read_books':
                books = Book.objects.filter(owner=request.user, status='okundu')
                count = books.count()
                if count == 0:
                    response_text = "Şu ana kadar okuduğun kitap bulunmuyor. Hadi yeni bir kitap ekleyelim!"
                else:
                    book_titles = ", ".join([b.title for b in books])
                    response_text = f"Şu ana kadar toplam {count} kitap okudun. İşte okuduğun kitaplar: {book_titles}"
                    
            elif action == 'to_read_books':
                books = Book.objects.filter(owner=request.user, status='okunacak')
                count = books.count()
                if count == 0:
                    response_text = "Okunacaklar listende kitap bulunmuyor."
                else:
                    book_titles = ", ".join([b.title for b in books])
                    response_text = f"Okuma sırana eklediğin {count} kitap var: {book_titles}"
                    
            elif action == 'all_books':
                books = Book.objects.filter(owner=request.user)
                if not books.exists():
                    response_text = "Kütüphanende henüz hiç kitap yok."
                else:
                    status_dict = {'okundu': 'Okundu', 'okunuyor': 'Okunuyor', 'okunacak': 'Okunacak'}
                    book_list = [f"{b.title} ({status_dict.get(b.status, b.status)})" for b in books]
                    response_text = "Kütüphanendeki tüm kitaplar:\n- " + "\n- ".join(book_list)
                    
            elif action == 'recommend_books':
                user_book_titles = set(Book.objects.filter(owner=request.user).values_list('title', flat=True))
                classics = [
                    "İlahi Komedi - Dante Alighieri",
                    "Anna Karenina - Lev Tolstoy",
                    "Don Kişot - Cervantes",
                    "Gurur ve Önyargı - Jane Austen",
                    "Küçük Prens - Antoine de Saint-Exupéry",
                    "Yüzyıllık Yalnızlık - Gabriel García Márquez",
                    "Vadideki Zambak - Honoré de Balzac",
                    "Bülbülü Öldürmek - Harper Lee"
                ]
                
                recommended = []
                for classic in classics:
                    title_only = classic.split(" - ")[0]
                    already_have = False
                    for u_title in user_book_titles:
                        if title_only.lower() in u_title.lower():
                            already_have = True
                            break
                    if not already_have:
                        recommended.append(classic)
                
                import random
                if len(recommended) > 3:
                    recommended = random.sample(recommended, 3)
                
                if recommended:
                    response_text = "İşte sana özel birkaç harika dünya klasiği önerisi:\n- " + "\n- ".join(recommended)
                else:
                    response_text = "Harikasın! Görünen o ki sana önerebileceğim tüm popüler klasikleri çoktan kütüphanene eklemişsin."
                    
            elif action == 'password_help':
                response_text = "Şifreni sıfırlamak için:\n1. Giriş sayfasındaki 'Şifremi Unuttum' linkine tıkla.\n2. Kayıtlı e-posta adresini gir.\n3. Gelen e-postadaki linke tıklayıp yeni şifreni belirle.\n\nVeya doğrudan şu adresi ziyaret et: /password-reset/"
                
            else:
                response_text = "Üzgünüm, bu komutu anlayamadım."
                
            return JsonResponse({'status': 'success', 'response': response_text})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)