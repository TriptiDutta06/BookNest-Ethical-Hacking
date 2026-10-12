"""
Test suite for BookNest — College Used-Book Marketplace
Verifies all 14 routes and both DEMO and SECURE modes.
"""

from app import app, init_db
import app as app_module

def run_tests():
    init_db()
    client = app.test_client()

    print("--- 1. Testing Storefront & Navigation ---")
    r = client.get('/')
    assert r.status_code == 200, f"Home failed: {r.status_code}"
    print("[PASS] Home Page (/) -> 200 OK")

    r = client.get('/about')
    assert r.status_code == 200, f"About failed: {r.status_code}"
    print("[PASS] About Page (/about) -> 200 OK")

    r = client.get('/browse')
    assert r.status_code == 200
    print("[PASS] Browse Page (/browse) -> 200 OK")

    r = client.get('/browse?q=Java')
    assert r.status_code == 200
    assert b'Java: The Complete Reference' in r.data
    print("[PASS] Normal Search ('Java') -> 200 OK, finds matching textbook")

    r = client.get('/book/1')
    assert r.status_code == 200
    assert b'Herbert Schildt' in r.data
    print("[PASS] Book Detail (/book/1) -> 200 OK")

    print("\n--- 2. Testing DEMO MODE Vulnerabilities (SECURITY_DEMO_MODE = True) ---")
    app_module.SECURITY_DEMO_MODE = True

    # Vulnerability 1: Reflected XSS
    xss_payload = '<script>alert("BookNest XSS")</script>'
    r = client.get(f'/browse?q={xss_payload}')
    assert r.status_code == 200
    assert xss_payload.encode('utf-8') in r.data
    print("[PASS] Reflected XSS Test: Raw unescaped JavaScript payload rendered in response!")

    # Vulnerability 2: SQL Injection Login Bypass
    sqli_payload = "' OR '1'='1' --"
    r = client.post('/login', data={'username_or_email': sqli_payload, 'password': 'any_password'}, follow_redirects=True)
    assert r.status_code == 200
    assert b'Welcome back' in r.data
    print("[PASS] SQL Injection Login Test: Bypassed password check with payload: ' OR '1'='1' --")

    # Logout
    client.get('/logout')

    # Normal valid login
    r = client.post('/login', data={'username_or_email': 'student@booknest.local', 'password': 'student123'}, follow_redirects=True)
    assert r.status_code == 200
    assert b'Aarav Sharma' in r.data
    print("[PASS] Normal Student Login: Authenticated as Aarav Sharma (user_id=2)")

    # Vulnerability 3: IDOR
    # Aarav Sharma is user 2. Order 2 belongs to user 3 (Rahul Deshmukh).
    r = client.get('/order/2')
    assert r.status_code == 200
    assert b'ORD-1002' in r.data
    assert b'Rahul Deshmukh' in r.data
    print("[PASS] IDOR Access Test: Logged in student accessed Order #2 belonging to Rahul Deshmukh!")

    print("\n--- 3. Testing E-Commerce Workflow (Cart, Checkout, Sell, Dashboard) ---")
    # Add to cart
    client.get('/cart/add/1', follow_redirects=True)
    r = client.get('/cart')
    assert b'Java: The Complete Reference' in r.data
    print("[PASS] Add to Cart and View Cart -> OK")

    # Checkout
    r = client.post('/checkout', data={
        'delivery_location': 'Central Campus Library - Desk 4',
        'payment_method': 'Campus UPI / QR Code on Meetup'
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b'Receipt & Handover Voucher' in r.data
    print("[PASS] Campus Checkout and Order Placement -> OK")

    # My Orders
    r = client.get('/orders')
    assert r.status_code == 200
    assert b'Central Campus Library' in r.data
    print("[PASS] My Orders List -> OK")

    # Wishlist
    client.get('/wishlist/add/2', follow_redirects=True)
    r = client.get('/wishlist')
    assert b'Computer Networks' in r.data
    print("[PASS] Wishlist Add & View -> OK")

    # Sell a book
    r = client.post('/sell', data={
        'title': 'Compiler Design Principles',
        'author': 'Alfred V. Aho',
        'category': 'Computer Science',
        'price': '340',
        'original_price': '850',
        'condition': 'Very Good',
        'description': 'Dragon book for CS Semester 6 compiler course.'
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b'Compiler Design Principles' in r.data
    print("[PASS] Sell a Book -> OK")

    # Seller Dashboard
    r = client.get('/seller-dashboard')
    assert r.status_code == 200
    assert b'Compiler Design Principles' in r.data
    print("[PASS] Seller Dashboard -> OK")

    # Profile
    r = client.get('/profile')
    assert r.status_code == 200
    assert b'student@booknest.local' in r.data
    print("[PASS] Student Profile -> OK")

    print("\n--- 4. Testing SECURE MODE Remediations (SECURITY_DEMO_MODE = False) ---")
    app_module.SECURITY_DEMO_MODE = False

    # Retest 1: XSS safely escaped
    r = client.get(f'/browse?q={xss_payload}')
    assert r.status_code == 200
    assert b'&lt;script&gt;alert(&#34;BookNest XSS&#34;)&lt;/script&gt;' in r.data or b'&lt;script&gt;' in r.data
    assert xss_payload.encode('utf-8') not in r.data
    print("[PASS] Remediation 1 (XSS Fixed): HTML script tag was escaped into safe entities!")

    # Retest 2: SQL Injection blocked
    client.get('/logout')
    r = client.post('/login', data={'username_or_email': sqli_payload, 'password': 'any_password'}, follow_redirects=True)
    assert b'Invalid username/email or password.' in r.data
    print("[PASS] Remediation 2 (SQLi Fixed): Parameterized query treated input as literal string and rejected login!")

    # Retest 3: IDOR blocked
    client.post('/login', data={'username_or_email': 'student@booknest.local', 'password': 'student123'}, follow_redirects=True)
    r = client.get('/order/2')
    assert r.status_code == 403
    print("[PASS] Remediation 3 (IDOR Fixed): Unauthorized order access blocked with HTTP 403 Forbidden!")

    print("\n" + "=" * 60)
    print("ALL 18 TEST CASES PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
