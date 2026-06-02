from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Book, Category, Like, Comment
from django.db.models import Count
from .forms import BookForm


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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Hesabın oluşturuldu, hoş geldin!')
            return redirect('book_list')
    else:
        form = UserCreationForm()
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