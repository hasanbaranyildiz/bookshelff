import json
import requests
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
    
    # Görüntülenme sayısını artır
    book.views_count += 1
    book.save(update_fields=['views_count'])
    
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
        form = BookForm(request.POST, request.FILES)
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
        form = BookForm(request.POST, request.FILES, instance=book)
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


@login_required
def book_search_api(request):
    """Google Books API üzerinden kitap arama"""
    query = request.GET.get('q', '')
    books_data = []
    
    if query:
        url = f"https://www.dr.com.tr/search?q={query}"
    else:
        url = "https://www.dr.com.tr/search?q=dunya+klasikleri"
        
    try:
        import json
        from bs4 import BeautifulSoup
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all('div', class_='product-card')[:12]
            
            for item in items:
                gtm_data = item.get('data-gtm')
                title = "Bilinmeyen Başlık"
                author = "Bilinmeyen Yazar"
                
                if gtm_data:
                    try:
                        gtm_json = json.loads(gtm_data)
                        title = gtm_json.get('item_name', title)
                        author = gtm_json.get('author', author)
                    except:
                        pass
                        
                img_tag = item.find('img')
                thumbnail = ""
                if img_tag:
                    thumbnail = img_tag.get('data-src') or img_tag.get('src', '')
                    
                if not thumbnail and item.find('a', class_='js-search-prd-item'):
                    # Bazen resim child div içinde oluyor
                    inner_div = item.find('div', class_='js-prd-img-first')
                    if inner_div:
                        thumbnail = inner_div.get('data-image-url', '')
                        
                books_data.append({
                    'id': item.get('data-id', ''),
                    'title': title,
                    'author': author,
                    'description': 'D&R veritabanından çekildi.',
                    'thumbnail': thumbnail,
                })
    except requests.RequestException:
        pass
        
    return render(request, 'books/api_book_search.html', {'books': books_data, 'query': query})


@login_required
def add_api_book(request):
    """API'den gelen verilerle otomatik kitap ekleme"""
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description')
        
        thumbnail_url = request.POST.get('thumbnail')
        
        category, created = Category.objects.get_or_create(name='Genel')
        
        book = Book.objects.create(
            title=title,
            author=author,
            description=description,
            category=category,
            owner=request.user,
            status='okunacak'
        )
        
        if thumbnail_url:
            from django.core.files.base import ContentFile
            import requests
            try:
                img_response = requests.get(thumbnail_url)
                if img_response.status_code == 200:
                    book.cover_image.save(f"api_cover_{book.id}.jpg", ContentFile(img_response.content), save=True)
            except Exception as e:
                pass
        messages.success(request, f'"{title}" kütüphanenize eklendi!')
        return redirect('book_list')
        
    return redirect('book_search_api')

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