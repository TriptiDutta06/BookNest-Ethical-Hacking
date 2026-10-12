# BookNest — College Used-Book Marketplace
### Academic Web Application & Ethical Hacking Security Assessment (15-Mark Project)

BookNest is an authentic, full-featured peer-to-peer textbook marketplace built for college students to buy, sell, and exchange course textbooks on campus. 

The application is styled with a warm, modern bookstore aesthetic and contains **zero** cybersecurity lab or hacker simulator banners on the customer-facing interface. The ethical hacking assessment is conducted through normal application features, followed by demonstrated remediation and retesting.

---

## Technology Stack

- **Backend**: Python 3.x, Flask (v3.0+)
- **Database**: SQLite3 (`database/booknest.db`) with Foreign Key support
- **Frontend**: HTML5, Semantic CSS3 (custom warm bookstore design system), Vanilla JavaScript
- **Templating**: Jinja2 (with auto-escaping & controlled demonstration filter)
- **Security & Hashing**: Werkzeug (`generate_password_hash`, `check_password_hash`)
- **Host & Port**: Strictly `http://127.0.0.1:5000` (Localhost only)

---

## Directory Structure

```text
BookNest/
│
├── app.py                      # Core Flask application with toggleable security modes
├── requirements.txt            # Python dependencies
├── run.bat                     # One-click Windows launcher
├── test_booknest.py            # Automated test suite (verifies 18 tests in both modes)
├── README.md                   # Project overview & running instructions
├── SECURITY_ASSESSMENT.md      # Comprehensive ethical hacking assessment report
├── PROJECT_EXPLANATION.md      # Detailed academic project documentation
├── VIVA_QA.md                  # 25+ Viva exam questions & answers
│
├── database/
│   └── booknest.db             # SQLite database (auto-created and seeded on first run)
│
├── static/
│   ├── css/
│   │   └── style.css           # Warm modern bookstore CSS design system
│   └── js/
│       ├── script.js           # Client-side toast notifications and alert interactions
│       └── main.js             # Legacy alias for backward compatibility
│
└── templates/
    ├── base.html               # Shared responsive layout with navbar & campus footer
    ├── index.html              # Homepage (Hero, statistics, categories, popular books)
    ├── browse.html             # Catalog & search (Reflected XSS demo location)
    ├── book_detail.html        # Book description, condition, seller profile, actions
    ├── login.html              # Student login (SQL Injection demo location)
    ├── register.html           # Student registration with hashed passwords
    ├── profile.html            # Student profile & activity overview
    ├── wishlist.html           # Saved textbooks wishlist
    ├── cart.html               # Shopping cart & subtotal calculation
    ├── checkout.html           # Campus meetup drop-point & payment selection
    ├── orders.html             # List of authenticated user orders
    ├── order_detail.html       # Order receipt & handover details (IDOR demo location)
    ├── sell.html               # Student textbook listing form
    ├── seller_dashboard.html   # Manage listed books & toggle sold status
    └── about.html              # Campus mission & safe handoff policy
```

---

## How to Install & Run

### 1. Prerequisites
Ensure Python 3 is installed.

### 2. Install Dependencies
Open your terminal in the project directory (`c:\ethiproject\CyberVault`):
```powershell
py -m pip install -r requirements.txt
```
*(or `pip install -r requirements.txt`)*

### 3. Start the Server
```powershell
py app.py
```
*(or double-click `run.bat`)*

### 4. Access the Marketplace
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## Pre-Seeded Demo Accounts & Data

The database initializes automatically on first run with realistic student accounts and 10 course textbooks:

| Role | Email | Username | Password | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Student** | `student@booknest.local` | `student` | `student123` | Owns Order #ORD-1001 (Record ID: 1) |
| **Peer** | `rahul@booknest.local` | `rahul` | `rahul123` | Owns Order #ORD-1002 (Record ID: 2) |
| **Senior** | `priya@booknest.local` | `priya` | `priya123` | Owns Order #ORD-1003 (Record ID: 3) |
| **Advisor** | `admin@booknest.local` | `admin` | `admin123` | CS Faculty Advisor account |

---

## Ethical Hacking Demonstration

The project incorporates **3 controlled educational vulnerabilities** integrated into normal e-commerce features:

### 1. Reflected XSS (Cross-Site Scripting)
- **Feature**: Book Search Bar (`/browse?q=`)
- **Vulnerability**: User input in `q` is reflected without escaping in the search results message.
- **Harmless PoC**:
  ```text
  <script>alert("BookNest XSS")</script>
  ```
- **Result in Demo Mode**: The script executes harmlessly in the browser.
- **Remediation**: Escaping via Jinja2 default auto-escaping (`{{ search_query }}`).
- **Result in Secure Mode**: Renders safely as literal text: `&lt;script&gt;alert("BookNest XSS")&lt;/script&gt;`.

### 2. SQL Injection (Authentication Bypass)
- **Feature**: Student Login (`/login`)
- **Vulnerability**: Unsafe string formatting in SQL query.
- **Educational PoC**:
  ```text
  Username / Email: ' OR '1'='1' --
  Password: (any text)
  ```
- **Result in Demo Mode**: SQLite comments out password verification and logs into the account.
- **Remediation**: Parameterized queries with placeholder `?` and Werkzeug password hash verification.
- **Result in Secure Mode**: Injection string is treated as literal data; login safely rejected with "Invalid credentials".

### 3. IDOR (Insecure Direct Object Reference)
- **Feature**: Order Receipt (`/order/<order_id>`)
- **Vulnerability**: Missing user ownership check on requested order ID.
- **Testing Procedure**:
  1. Log in as `student@booknest.local` (User ID: 2).
  2. View your own order at `http://127.0.0.1:5000/order/1`.
  3. Change the URL to `http://127.0.0.1:5000/order/2`.
- **Result in Demo Mode**: Unauthorized access to Rahul's order (User ID: 3) is displayed.
- **Remediation**: Server-side authorization check:
  ```python
  if order['user_id'] != session['user_id']:
      return "Forbidden", 403
  ```
- **Result in Secure Mode**: Access is blocked with HTTP 403 Forbidden.

---

## How to Switch Between Modes

At line 26 of `app.py`:

```python
# True  = Educational demonstration mode (vulnerabilities active for testing)
# False = Secure mode (Parameterized queries, Jinja2 escaping, Authorization checks)
SECURITY_DEMO_MODE = True
```

- Change `SECURITY_DEMO_MODE = False` and save the file.
- Flask automatically reloads the application.
- Retest all three vulnerabilities to confirm that all security flaws have been fixed!

---

## Automated Verification

Run the automated 18-test verification script to validate all pages and security modes:
```powershell
py test_booknest.py
```
