# Bookshelf: Premium Social Library 📚

Bookshelf is a fully-featured, premium-designed Django web application that allows users to manage their personal book collections while interacting with a broader community through an Instagram-style social feed. This project serves as a comprehensive Term Project demonstrating full-stack Django capabilities.

![Bookshelf Feed Concept](https://img.shields.io/badge/UI-Premium_Glassmorphism-purple.svg)
![Django Version](https://img.shields.io/badge/Django-5.0+-green.svg)

## 🌟 Core Features
- **Authentication System**: Secure user registration, login, and session management.
- **CRUD Operations**: Users can Create, Read, Update, and Delete their personal book library entries.
- **Social "Keşfet" Feed**: An engaging, vertically-scrolling Instagram-style social feed where users can see what others are reading.
- **Interactive Review System**: Users can Like (❤️) books directly from the feed. When commenting, users are required to explicitly mark a book as "Recommended" (👍) or "Not Recommended" (👎), powering a dynamic recommendation percentage algorithm.
- **Search & Filter**: Find books instantly by title, reading status (Read, Reading, To Read), or Category.
- **Premium UI/UX**: Built with Bootstrap 5, featuring deep black backgrounds (`#000000`), sleek radial gradients, and elegant typography (`Playfair Display`).

## 🏗️ Technical Architecture & Database Design
The application is built entirely on the Django Framework utilizing the MVT (Model-View-Template) pattern.

### Models
1. **User**: Built-in Django authentication model.
2. **Category**: Groups books by genre.
3. **Book**: The core model containing `title`, `author`, `description`, `status`. Relates to `User` (owner) and `Category`.
4. **Like**: A tracking model with a `unique_together` constraint on `(user, book)` to prevent duplicate likes.
5. **Comment**: Stores user reviews and a critical `is_recommended` boolean field used to calculate the community approval rate.

### Optimization
To prevent the notorious "N+1 query problem" in the Social Feed, the system uses advanced ORM optimization techniques:
- `annotate()` with `Count` to calculate likes and comments directly in the database.
- `prefetch_related()` to load the newest comments associated with multiple books in a single query.

## 🚀 Local Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hasanbaranyildiz/bookshelff.git
   cd bookshelff
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

4. **Seed the database (Optional)**
   Run the seed script to automatically create an admin account (`admin` / `baranaziz123`) and load 5 World Classics with dummy reviews.
   ```bash
   python seed_classics.py
   ```

5. **Run the server**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000`

## 🧪 Testing
The project includes comprehensive automated Unit Tests to verify core functionality, views, and database interactions.
Run the tests using:
```bash
python manage.py test
```

## 🌍 Deployment (Render)
This application is fully production-ready and configured for deployment on PaaS providers like **Render**.
- `build.sh`: Automates dependency installation, static collection, and migrations.
- `Whitenoise`: Configured in `settings.py` for highly efficient static file serving.
- `Gunicorn`: Ready to be used as the WSGI HTTP Server.

**Render Start Command:** `gunicorn config.wsgi:application`

---
*Developed as a Django Term Project.*
