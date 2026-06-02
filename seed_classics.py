import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from books.models import Category, Book, Like, Comment

# 1. Create Admin User
admin_user, created = User.objects.get_or_create(username='admin')
if created:
    admin_user.set_password('baranaziz123')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print("Admin kullanıcısı oluşturuldu.")
else:
    admin_user.set_password('baranaziz123')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print("Admin şifresi baranaziz123 olarak güncellendi.")

# Dummy Users for comments
user1, _ = User.objects.get_or_create(username='kitapkurdu', email='k@k.com')
user1.set_password('123')
user1.save()
user2, _ = User.objects.get_or_create(username='edebiyatsever', email='e@e.com')
user2.set_password('123')
user2.save()
user3, _ = User.objects.get_or_create(username='okuyan_insan', email='o@o.com')
user3.set_password('123')
user3.save()

# 2. Create World Classics Category
category, _ = Category.objects.get_or_create(name='Dünya Klasikleri')

classics = [
    {"title": "Suç ve Ceza", "author": "Fyodor Dostoyevski", "desc": "Rus edebiyatının başyapıtlarından biri. İnsanın iç dünyasını, vicdan azabını ve kurtuluş arayışını anlatan derin bir eser."},
    {"title": "1984", "author": "George Orwell", "desc": "Büyük Birader'in her şeyi izlediği, düşünce özgürlüğünün olmadığı distopik bir dünyayı anlatan efsanevi roman."},
    {"title": "Sefiller", "author": "Victor Hugo", "desc": "Jean Valjean'ın hikayesi üzerinden adalet, aşk ve toplumsal eşitsizlikleri sorgulayan Fransız edebiyatı başyapıtı."},
    {"title": "Satranç", "author": "Stefan Zweig", "desc": "Nazilerden kaçan bir adamın gemide rastladığı bir satranç şampiyonu ile yaşadığı psikolojik gerilimi anlatan kısa ama etkili kitap."},
    {"title": "Simyacı", "author": "Paulo Coelho", "desc": "Kendi efsanesini, hazinesini bulmak için Mısır piramitlerine doğru yola çıkan çoban Santiago'nun felsefi hikayesi."},
]

for item in classics:
    book, b_created = Book.objects.get_or_create(
        title=item["title"],
        owner=admin_user,
        defaults={
            'author': item["author"],
            'description': item["desc"],
            'category': category,
            'status': 'okundu'
        }
    )
    if b_created:
        print(f"Eklendi: {item['title']}")
        # Add random comments & likes
        Comment.objects.create(user=user1, book=book, content="Kesinlikle herkesin hayatında bir kez okuması gereken bir başyapıt!", is_recommended=True)
        Comment.objects.create(user=user2, book=book, content="Okurken çok düşündürdü, betimlemeler harika.", is_recommended=True)
        Like.objects.create(user=user1, book=book)
        Like.objects.create(user=user2, book=book)
        Like.objects.create(user=user3, book=book)
        if item["title"] in ["1984", "Suç ve Ceza"]:
            Comment.objects.create(user=user3, book=book, content="Beni çok etkiledi ama dili biraz ağır, alışmak zaman alıyor.", is_recommended=False)

print("Tüm dünya klasikleri başarıyla eklendi!")
