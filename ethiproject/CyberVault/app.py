"""
BookNest — College Used-Book Marketplace
=========================================
Academic Ethical Hacking Web Application & Security Assessment Project.
Strictly designed for authorized academic demonstration on localhost: http://127.0.0.1:5000

Educational Vulnerabilities Demonstrated:
1. Reflected XSS (Book Search)
2. SQL Injection (Login Authentication Bypass)
3. Insecure Direct Object Reference / IDOR (Order Access Control)

Toggle SECURITY_DEMO_MODE below:
- True: Educational demonstration mode (vulnerabilities active for testing)
- False: Secure production-ready mode (all vulnerabilities remediated)
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

# ==============================================================================
# SECURITY MODE TOGGLE
# ==============================================================================
# True  = Vulnerabilities active for controlled localhost demonstration
# False = Secure mode (Parameterized queries, Jinja2 escaping, Authorization checks)
SECURITY_DEMO_MODE = True

app = Flask(__name__)
app.secret_key = "booknest-academic-secret-key-2026-safe-local"

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
DB_PATH = os.path.join(DB_DIR, 'booknest.db')

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)


# ==============================================================================
# DATABASE CONNECTION & INITIALIZATION
# ==============================================================================
def get_db():
    """Returns a SQLite connection with Row factory enabled for dictionary-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Creates tables and seeds initial realistic dummy books, users, and orders."""
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        password_plain TEXT NOT NULL,
        full_name TEXT NOT NULL,
        department TEXT DEFAULT 'Computer Science',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Books Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        original_price INTEGER NOT NULL,
        condition TEXT NOT NULL,
        condition_slug TEXT NOT NULL,
        cover_theme TEXT NOT NULL,
        is_available INTEGER DEFAULT 1,
        is_popular INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(seller_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 3. Wishlist Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, book_id),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
    );
    """)

    # 4. Cart Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, book_id),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
    );
    """)

    # 5. Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_number TEXT NOT NULL,
        total_amount INTEGER NOT NULL,
        delivery_location TEXT NOT NULL,
        status TEXT DEFAULT 'Confirmed',
        payment_method TEXT DEFAULT 'Campus UPI / Cash on Meetup',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 6. Order Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        price INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
    );
    """)

    # Seed Initial Users if table empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        demo_users = [
            ("admin", "admin@booknest.local", generate_password_hash("admin123"), "admin123", "Prof. Vikram Malhotra", "CS Faculty Advisor"),
            ("student", "student@booknest.local", generate_password_hash("student123"), "student123", "Aarav Sharma", "Computer Science (Sem 5)"),
            ("rahul", "rahul@booknest.local", generate_password_hash("rahul123"), "rahul123", "Rahul Deshmukh", "Information Technology (Sem 4)"),
            ("priya", "priya@booknest.local", generate_password_hash("priya123"), "priya123", "Priya Nair", "Data Science (Sem 6)"),
        ]
        cursor.executemany("""
        INSERT INTO users (username, email, password_hash, password_plain, full_name, department)
        VALUES (?, ?, ?, ?, ?, ?);
        """, demo_users)

    # Seed Initial Books if table empty
    cursor.execute("SELECT COUNT(*) FROM books;")
    if cursor.fetchone()[0] == 0:
        demo_books = [
            (2, "Java: The Complete Reference", "Herbert Schildt", "Computer Science",
             "Comprehensive guide for Java SE 11. Covers OOP concepts, multithreading, collections framework, and lambda expressions. Includes handwritten notes for semester exam.",
             380, 895, "Like New", "like-new", "cs", 1, 1),
            (3, "Computer Networks: A Top-Down Approach", "James F. Kurose & Keith W. Ross", "Computer Science",
             "Standard networking book focusing on application down to physical layer. Used for CS 301. Minimal markings in Chapter 4.",
             420, 950, "Very Good", "very-good", "cs", 1, 1),
            (2, "Database System Concepts", "Abraham Silberschatz & Henry F. Korth", "Computer Science",
             "Standard DBMS syllabus textbook covering Relational Algebra, SQL queries, Normalization (1NF to BCNF), and Transaction concurrency control.",
             350, 820, "Good", "good", "cs", 1, 1),
            (4, "Artificial Intelligence: A Modern Approach", "Stuart Russell & Peter Norvig", "Data Science",
             "Classic textbook on intelligent agents, informed heuristic search (A*), game trees, probabilistic reasoning, and modern reinforcement learning.",
             550, 1250, "Like New", "like-new", "ds", 1, 1),
            (3, "Web Technologies: HTML, CSS, JS & PHP", "Uttam K. Roy", "Web Development",
             "Complete college reference textbook covering frontend basics, DOM scripting, responsive design, and backend development with PHP/MySQL.",
             290, 650, "Very Good", "very-good", "web", 1, 0),
            (4, "Data Science Fundamentals with Python", "Jake VanderPlas", "Data Science",
             "Covers essential data libraries: NumPy, Pandas, Matplotlib, Scikit-Learn. Perfect for lab practicals and minor data analysis projects.",
             460, 990, "Like New", "like-new", "ds", 1, 0),
            (2, "Operating System Concepts", "Silberschatz, Galvin & Gagne", "Computer Science",
             "The popular dinosaur book for OS. Explains process synchronization, CPU scheduling algorithms, virtual memory paging, and Linux kernel structure.",
             390, 850, "Good", "good", "cs", 1, 0),
            (3, "Cybersecurity Essentials", "William Stallings", "Engineering",
             "Covers network defense, encryption standards, authentication protocols, secure coding principles, and web application threat models.",
             370, 780, "Fair", "fair", "eng", 1, 0),
            (4, "Software Engineering: A Practitioner's Approach", "Roger S. Pressman", "Engineering",
             "Covers agile models, software design architectures, requirement engineering, testing strategies, and project management fundamentals.",
             410, 890, "Good", "good", "eng", 1, 0),
            (2, "Discrete Mathematics and Its Applications", "Kenneth H. Rosen", "Mathematics",
             "Standard text for CS math covering Propositional Logic, Graph Theory, Combinatorics, and Proof techniques.",
             340, 750, "Very Good", "very-good", "math", 1, 0),
        ]
        cursor.executemany("""
        INSERT INTO books (seller_id, title, author, category, description, price, original_price, condition, condition_slug, cover_theme, is_available, is_popular)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, demo_books)

    # Seed Initial Orders for IDOR Demonstration if table empty
    cursor.execute("SELECT COUNT(*) FROM orders;")
    if cursor.fetchone()[0] == 0:
        demo_orders = [
            (2, "ORD-1001", 380, "Central Campus Library - Desk 4", "Confirmed", "Campus UPI / Cash on Meetup"),
            (3, "ORD-1002", 350, "Student Canteen - Table 12", "Confirmed", "Cash on Campus Handoff"),
            (4, "ORD-1003", 550, "Innovation Hub - Reception", "Confirmed", "Campus UPI"),
        ]
        cursor.executemany("""
        INSERT INTO orders (user_id, order_number, total_amount, delivery_location, status, payment_method)
        VALUES (?, ?, ?, ?, ?, ?);
        """, demo_orders)

        # Seed items corresponding to orders
        demo_items = [
            (1, 1, 380, 1),  # Order 1 (belongs to student user_id=2): Book 1 (Java)
            (2, 3, 350, 1),  # Order 2 (belongs to rahul user_id=3): Book 3 (DBMS)
            (3, 4, 550, 1),  # Order 3 (belongs to priya user_id=4): Book 4 (AI)
        ]
        cursor.executemany("""
        INSERT INTO order_items (order_id, book_id, price, quantity)
        VALUES (?, ?, ?, ?);
        """, demo_items)

    conn.commit()
    conn.close()


# Initialize database automatically
init_db()


# ==============================================================================
# TEMPLATE CONTEXT PROCESSOR (Dynamic Header Badges & User Status)
# ==============================================================================
@app.context_processor
def inject_global_data():
    """Injects cart count, wishlist count, demo mode flag, and current user info into every template."""
    user_id = session.get('user_id')
    cart_count = 0
    wishlist_count = 0
    current_user = None

    if user_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        current_user = cursor.fetchone()

        cursor.execute("SELECT SUM(quantity) FROM cart WHERE user_id = ?", (user_id,))
        res = cursor.fetchone()[0]
        cart_count = res if res else 0

        cursor.execute("SELECT COUNT(*) FROM wishlist WHERE user_id = ?", (user_id,))
        wishlist_count = cursor.fetchone()[0]
        conn.close()

    return {
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
        "current_user": current_user,
        "SECURITY_DEMO_MODE": SECURITY_DEMO_MODE,
    }


# ==============================================================================
# MAIN STORE PAGES
# ==============================================================================

@app.route('/')
def index():
    """Home page displaying hero banner, statistics, category list, popular and recent books."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT b.*, u.full_name as seller_name, u.department as seller_dept
    FROM books b
    JOIN users u ON b.seller_id = u.id
    WHERE b.is_available = 1 AND b.is_popular = 1
    LIMIT 4;
    """)
    popular_books = cursor.fetchall()

    cursor.execute("""
    SELECT b.*, u.full_name as seller_name, u.department as seller_dept
    FROM books b
    JOIN users u ON b.seller_id = u.id
    WHERE b.is_available = 1 AND b.is_popular = 0
    ORDER BY b.id DESC
    LIMIT 4;
    """)
    recent_books = cursor.fetchall()

    conn.close()
    return render_template('index.html', popular_books=popular_books, recent_books=recent_books)


@app.route('/browse')
def browse():
    """
    Catalog browse page with category filter and search query support.
    
    ----------------------------------------------------------------------------
    ETHICAL HACKING VULNERABILITY #1 — REFLECTED XSS
    ----------------------------------------------------------------------------
    When SECURITY_DEMO_MODE = True:
      The search query parameter `q` is reflected unsafely in `browse.html`
      using the Jinja2 `| safe` filter, allowing the educational PoC:
      <script>alert("BookNest XSS")</script> to execute in the browser.
      
    When SECURITY_DEMO_MODE = False:
      The search query is safely escaped by Jinja2's default context-aware
      auto-escaping mechanism, preventing script execution and displaying safe text.
    ----------------------------------------------------------------------------
    """
    category_filter = request.args.get('category', '').strip()
    search_query = request.args.get('q', '').strip()

    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT b.*, u.full_name as seller_name, u.department as seller_dept
    FROM books b
    JOIN users u ON b.seller_id = u.id
    WHERE b.is_available = 1
    """
    params = []

    if category_filter:
        query += " AND LOWER(b.category) = LOWER(?)"
        params.append(category_filter)

    if search_query:
        query += " AND (LOWER(b.title) LIKE LOWER(?) OR LOWER(b.author) LIKE LOWER(?) OR LOWER(b.category) LIKE LOWER(?))"
        term = f"%{search_query}%"
        params.extend([term, term, term])

    query += " ORDER BY b.id DESC;"
    cursor.execute(query, params)
    books = cursor.fetchall()
    conn.close()

    return render_template(
        'browse.html',
        books=books,
        category_filter=category_filter,
        search_query=search_query,
        demo_mode=SECURITY_DEMO_MODE
    )


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """Book detail page showing description, condition, seller profile, and action buttons."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT b.*, u.full_name as seller_name, u.department as seller_dept, u.email as seller_email
    FROM books b
    JOIN users u ON b.seller_id = u.id
    WHERE b.id = ?;
    """, (book_id,))
    book = cursor.fetchone()
    conn.close()

    if not book:
        flash("Textbook not found in campus database.", "danger")
        return redirect(url_for('browse'))

    return render_template('book_detail.html', book=book)


@app.route('/about')
def about():
    """About BookNest page explaining student mission and safe meetup policies."""
    return render_template('about.html')


# ==============================================================================
# AUTHENTICATION (Register, Login, Logout)
# ==============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration route storing password using Werkzeug password hashing."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        department = request.form.get('department', 'Computer Science').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password or not full_name:
            flash("Please fill in all required fields.", "warning")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        conn = get_db()
        cursor = conn.cursor()

        # Check existing user
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            conn.close()
            flash("Username or Email already registered. Please login.", "warning")
            return redirect(url_for('login'))

        # Securely hash password
        pwd_hash = generate_password_hash(password)
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, password_plain, full_name, department)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (username, email, pwd_hash, password, full_name, department))
        conn.commit()
        conn.close()

        flash("Registration successful! You can now log in with your credentials.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Student login route.
    
    ----------------------------------------------------------------------------
    ETHICAL HACKING VULNERABILITY #2 — SQL INJECTION
    ----------------------------------------------------------------------------
    When SECURITY_DEMO_MODE = True:
      Demonstrates authentication bypass via unsafe SQL string concatenation:
      `SELECT * FROM users WHERE (email = '{user_input}' OR username = '{user_input}') AND password_plain = '{password}'`
      
      Educational PoC:
      Username: ' OR '1'='1' --
      Password: (anything)
      The comment syntax `--` truncates password verification, matching the
      first user record in SQLite and granting unauthorized access.
      
    When SECURITY_DEMO_MODE = False:
      Uses secure parameterized queries:
      `SELECT * FROM users WHERE email = ? OR username = ?`
      and verifies the password using `check_password_hash()`.
      The SQL injection string is safely treated as literal text and fails login.
    ----------------------------------------------------------------------------
    """
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        conn = get_db()
        cursor = conn.cursor()
        user = None

        if SECURITY_DEMO_MODE:
            # VULNERABLE DEMO IMPLEMENTATION:
            # Unsafe string concatenation allows classic SQL Injection authentication bypass.
            # Intended educational payloads:
            #   ' OR '1'='1' --
            #   admin@booknest.local' --
            try:
                vuln_query = f"SELECT * FROM users WHERE email = '{username_or_email}' AND password_plain = '{password}'"
                cursor.execute(vuln_query)
                user = cursor.fetchone()
                if not user:
                    # Also allow username lookup with same vulnerable concatenation
                    vuln_query_u = f"SELECT * FROM users WHERE username = '{username_or_email}' AND password_plain = '{password}'"
                    cursor.execute(vuln_query_u)
                    user = cursor.fetchone()
            except sqlite3.OperationalError as e:
                conn.close()
                flash(f"Database Query Error: {str(e)}", "danger")
                return render_template('login.html')
        else:
            # SECURE REMEDIATED IMPLEMENTATION: Parameterized queries + Password Hashing
            cursor.execute("SELECT * FROM users WHERE email = ? OR username = ?", (username_or_email, username_or_email))
            candidate = cursor.fetchone()
            if candidate and check_password_hash(candidate['password_hash'], password):
                user = candidate

        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_name'] = user['full_name']
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logs out student and clears session."""
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    """Displays user profile details and activity statistics."""
    if 'user_id' not in session:
        flash("Please log in to access your student profile.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM books WHERE seller_id = ?", (session['user_id'],))
    listed_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (session['user_id'],))
    orders_count = cursor.fetchone()[0]

    conn.close()
    return render_template('profile.html', user=user, listed_count=listed_count, orders_count=orders_count)


# ==============================================================================
# WISHLIST & CART
# ==============================================================================

@app.route('/wishlist')
def wishlist():
    """Displays user's saved wishlist books."""
    if 'user_id' not in session:
        flash("Please log in to view your wishlist.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT b.*, u.full_name as seller_name, u.department as seller_dept
    FROM wishlist w
    JOIN books b ON w.book_id = b.id
    JOIN users u ON b.seller_id = u.id
    WHERE w.user_id = ?
    ORDER BY w.id DESC;
    """, (session['user_id'],))
    wishlist_books = cursor.fetchall()
    conn.close()

    return render_template('wishlist.html', books=wishlist_books)


@app.route('/wishlist/add/<int:book_id>')
def wishlist_add(book_id):
    """Adds a textbook to wishlist."""
    if 'user_id' not in session:
        flash("Please log in to add books to your wishlist.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO wishlist (user_id, book_id) VALUES (?, ?)", (session['user_id'], book_id))
        conn.commit()
        flash("Book added to your Wishlist! ❤️", "success")
    except sqlite3.IntegrityError:
        flash("Book is already in your Wishlist.", "info")
    finally:
        conn.close()

    return redirect(request.referrer or url_for('browse'))


@app.route('/wishlist/remove/<int:book_id>')
def wishlist_remove(book_id):
    """Removes a book from wishlist."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishlist WHERE user_id = ? AND book_id = ?", (session['user_id'], book_id))
    conn.commit()
    conn.close()

    flash("Item removed from your wishlist.", "info")
    return redirect(url_for('wishlist'))


@app.route('/cart')
def cart():
    """Displays items in cart with subtotal calculation."""
    if 'user_id' not in session:
        flash("Please log in to access your shopping cart.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT c.id as cart_id, c.quantity, b.id as book_id, b.title, b.author, b.price, b.condition, b.category, b.cover_theme
    FROM cart c
    JOIN books b ON c.book_id = b.id
    WHERE c.user_id = ?;
    """, (session['user_id'],))
    items = cursor.fetchall()
    conn.close()

    subtotal = sum(item['price'] * item['quantity'] for item in items)
    return render_template('cart.html', items=items, subtotal=subtotal)


@app.route('/cart/add/<int:book_id>')
def cart_add(book_id):
    """Adds a book to the shopping cart."""
    if 'user_id' not in session:
        flash("Please log in to add items to your cart.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, quantity FROM cart WHERE user_id = ? AND book_id = ?", (session['user_id'], book_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE id = ?", (existing['id'],))
    else:
        cursor.execute("INSERT INTO cart (user_id, book_id, quantity) VALUES (?, ?, 1)", (session['user_id'], book_id))

    conn.commit()
    conn.close()
    flash("Book added to your Cart! 🛒", "success")
    return redirect(request.referrer or url_for('cart'))


@app.route('/cart/remove/<int:book_id>')
def cart_remove(book_id):
    """Removes a book from the shopping cart."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ? AND book_id = ?", (session['user_id'], book_id))
    conn.commit()
    conn.close()

    flash("Item removed from cart.", "info")
    return redirect(url_for('cart'))


# ==============================================================================
# CHECKOUT & ORDERS (Including IDOR Demonstration)
# ==============================================================================

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Dummy checkout page simulating campus meetup handoff and order confirmation."""
    if 'user_id' not in session:
        flash("Please log in to proceed to checkout.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT c.quantity, b.id as book_id, b.title, b.price
    FROM cart c
    JOIN books b ON c.book_id = b.id
    WHERE c.user_id = ?;
    """, (session['user_id'],))
    items = cursor.fetchall()

    if not items:
        conn.close()
        flash("Your cart is empty.", "warning")
        return redirect(url_for('browse'))

    subtotal = sum(item['price'] * item['quantity'] for item in items)

    if request.method == 'POST':
        pickup_location = request.form.get('delivery_location', 'Central Campus Library Desk').strip()
        payment_method = request.form.get('payment_method', 'Campus UPI / Cash on Meetup').strip()

        # Create new order
        import random
        order_num = f"ORD-{random.randint(1100, 9999)}"

        cursor.execute("""
        INSERT INTO orders (user_id, order_number, total_amount, delivery_location, status, payment_method)
        VALUES (?, ?, ?, ?, 'Confirmed', ?);
        """, (session['user_id'], order_num, subtotal, pickup_location, payment_method))
        order_id = cursor.lastrowid

        # Insert items
        for item in items:
            cursor.execute("""
            INSERT INTO order_items (order_id, book_id, price, quantity)
            VALUES (?, ?, ?, ?);
            """, (order_id, item['book_id'], item['price'], item['quantity']))

        # Clear cart
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (session['user_id'],))
        conn.commit()
        conn.close()

        flash(f"Order #{order_num} successfully placed! Meet your peer at {pickup_location}.", "success")
        return redirect(url_for('order_detail', order_id=order_id))

    conn.close()
    return render_template('checkout.html', items=items, subtotal=subtotal)


@app.route('/orders')
def orders():
    """Displays all past and active orders for the currently authenticated user."""
    if 'user_id' not in session:
        flash("Please log in to view your orders.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM orders
    WHERE user_id = ?
    ORDER BY id DESC;
    """, (session['user_id'],))
    user_orders = cursor.fetchall()
    conn.close()

    return render_template('orders.html', orders=user_orders)


@app.route('/order/<int:order_id>')
def order_detail(order_id):
    """
    Order receipt & status tracking page.
    
    ----------------------------------------------------------------------------
    ETHICAL HACKING VULNERABILITY #3 — IDOR / BROKEN ACCESS CONTROL
    ----------------------------------------------------------------------------
    When SECURITY_DEMO_MODE = True:
      Authorization check is missing. Any authenticated user can view another
      student's order receipt simply by changing the ID in the URL.
      Example: Student A (user 2) views /order/1. Changing the URL to
      /order/2 reveals Student B's order details without permission.
      
    When SECURITY_DEMO_MODE = False:
      Enforces strict ownership authorization:
      `if order['user_id'] != session['user_id']: abort(403)`
      Unauthorized attempts are blocked with a 403 Forbidden status.
    ----------------------------------------------------------------------------
    """
    if 'user_id' not in session:
        flash("Please log in to view order details.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT o.*, u.full_name as buyer_name, u.email as buyer_email, u.department as buyer_dept
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE o.id = ?;
    """, (order_id,))
    order = cursor.fetchone()

    if not order:
        conn.close()
        flash("Order not found.", "danger")
        return redirect(url_for('orders'))

    # ACCESS CONTROL VERIFICATION
    if not SECURITY_DEMO_MODE:
        # SECURE REMEDIATED IMPLEMENTATION: Verify current user owns the order
        if order['user_id'] != session['user_id']:
            conn.close()
            flash("Access Denied: You are not authorized to view this order.", "danger")
            return render_template('orders.html', orders=[]), 403

    # Fetch order items
    cursor.execute("""
    SELECT oi.*, b.title, b.author, b.condition, b.category
    FROM order_items oi
    JOIN books b ON oi.book_id = b.id
    WHERE oi.order_id = ?;
    """, (order_id,))
    items = cursor.fetchall()
    conn.close()

    return render_template('order_detail.html', order=order, items=items, demo_mode=SECURITY_DEMO_MODE)


# ==============================================================================
# SELLER FUNCTIONALITY (Sell a Book & Seller Dashboard)
# ==============================================================================

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    """Allows a logged-in student to list a textbook for sale on campus."""
    if 'user_id' not in session:
        flash("Please log in to list your used book for sale.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', 'Computer Science').strip()
        price = request.form.get('price', 0)
        original_price = request.form.get('original_price', 0)
        condition = request.form.get('condition', 'Good').strip()
        description = request.form.get('description', '').strip()

        if not title or not author or not price:
            flash("Please enter title, author, and selling price.", "warning")
            return render_template('sell.html')

        # Compute theme & slug
        condition_slug = condition.lower().replace(" ", "-")
        theme_map = {
            "Computer Science": "cs",
            "Data Science": "ds",
            "Web Development": "web",
            "Engineering": "eng",
            "Business": "biz",
            "Mathematics": "math"
        }
        cover_theme = theme_map.get(category, "cs")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO books (seller_id, title, author, category, description, price, original_price, condition, condition_slug, cover_theme, is_available, is_popular)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0);
        """, (session['user_id'], title, author, category, description, int(price), int(original_price or price), condition, condition_slug, cover_theme))
        new_book_id = cursor.lastrowid
        conn.commit()
        conn.close()

        flash("Your textbook listing is now live for other students on campus!", "success")
        return redirect(url_for('book_detail', book_id=new_book_id))

    return render_template('sell.html')


@app.route('/seller-dashboard')
def seller_dashboard():
    """Displays all textbooks currently listed or sold by the logged-in student."""
    if 'user_id' not in session:
        flash("Please log in to access your Seller Dashboard.", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM books
    WHERE seller_id = ?
    ORDER BY id DESC;
    """, (session['user_id'],))
    my_books = cursor.fetchall()
    conn.close()

    return render_template('seller_dashboard.html', books=my_books)


@app.route('/book/toggle-status/<int:book_id>')
def toggle_book_status(book_id):
    """Allows seller to mark a book as Available or Sold."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT seller_id, is_available FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()

    if book and book['seller_id'] == session['user_id']:
        new_status = 0 if book['is_available'] == 1 else 1
        cursor.execute("UPDATE books SET is_available = ? WHERE id = ?", (new_status, book_id))
        conn.commit()
        flash("Book status updated successfully.", "success")
    else:
        flash("Unauthorized action.", "danger")

    conn.close()
    return redirect(url_for('seller_dashboard'))


# ==============================================================================
# SERVER ENTRY POINT (Strictly http://127.0.0.1:5000)
# ==============================================================================
if __name__ == '__main__':
    print("=" * 60)
    print(" Starting BookNest — College Used-Book Marketplace")
    print(f" Security Demo Mode: {'ENABLED (Vulnerabilities Active)' if SECURITY_DEMO_MODE else 'DISABLED (Secure Production)'}")
    print(" Running strictly on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
