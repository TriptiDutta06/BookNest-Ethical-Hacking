# BookNest — College Used-Book Marketplace
## Academic Project Documentation (15-Mark Ethical Hacking Submission)

---

## 1. Problem Statement
Every academic year, college students purchase expensive textbooks for individual semester courses, spending between ₹3,000 and ₹6,000 per term. After final exams, these books often sit unused on dorm shelves, while incoming junior batches purchase the same titles brand-new. Existing online marketplaces charge high commission fees, require postal shipping that takes days, and lack student-to-student verification.

From a cybersecurity perspective, small community web portals developed without formal security audits frequently harbor critical security oversights, including cross-site scripting, SQL injection, and broken access control.

---

## 2. Proposed Solution
**BookNest** is a specialized peer-to-peer used textbook marketplace designed specifically for university campuses. It allows students to:
- Browse and search required textbooks by course department.
- Connect with classmates for zero-commission, hand-to-hand delivery in designated safe campus zones (Library, Cafeteria, Tech Hub).
- List surplus textbooks in under two minutes with condition ratings and course notes.

The platform was developed to model both a functional student enterprise and a controlled testbed for an authorized **Ethical Hacking Security Assessment**.

---

## 3. Project Objectives
1. **Functional Objectives**:
   - Deliver a responsive, intuitive e-commerce web application tailored to campus students.
   - Implement persistent data storage for user accounts, book catalogs, wishlists, carts, and order histories.
   - Maintain a warm bookstore design aesthetic without looking like a "hacking simulator".
2. **Security & Academic Objectives**:
   - Identify and demonstrate three major web application vulnerabilities in a controlled localhost environment:
     1. Reflected Cross-Site Scripting (XSS) in catalog search.
     2. SQL Injection (SQLi) in student authentication.
     3. Insecure Direct Object Reference (IDOR) in order tracking.
   - Formulate and deploy source-code remediations.
   - Retest to verify that vulnerabilities are fully neutralized.

---

## 4. System Modules
The BookNest system comprises five functional modules:

```text
┌─────────────────────────────────────────────────────────────┐
│                       BOOKNEST SYSTEM                       │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Storefront   │ Auth & User  │ Shopping &   │ Seller & Order │
│ Module       │ Module       │ Cart Module  │ Tracking       │
├──────────────┼──────────────┼──────────────┼────────────────┤
│ • Home Page  │ • Register   │ • Wishlist   │ • Sell Book    │
│ • Catalog    │ • Login      │ • Cart       │ • Dashboard    │
│ • Search     │ • Profile    │ • Checkout   │ • My Orders    │
│ • Details    │ • Logout     │ • Handover   │ • Receipt View │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

1. **Storefront & Catalog Module**:
   - Displays featured and recent books with course tags and condition indicators.
   - Enables keyword search across titles, authors, and departments.
2. **Authentication & Profile Module**:
   - Secure registration, password hashing (PBKDF2/SHA-256 via Werkzeug), and session-based login.
3. **Cart & Wishlist Module**:
   - Manages student selections, real-time quantity updates, and subtotal pricing.
4. **Checkout & Meetup Module**:
   - Simulates physical campus meetup selection and creates order records.
5. **Seller Management Module**:
   - Allows students to post textbooks, edit listings, and mark items as Available or Sold.

---

## 5. Technology Stack & Justification

| Technology | Role | Justification |
| :--- | :--- | :--- |
| **Python 3.14** | Core Language | Clean syntax, fast execution, excellent standard library. |
| **Flask 3.1** | Web Framework | Lightweight, modular WSGI micro-framework without bloat; ideal for educational code audits. |
| **SQLite3** | Relational Database | Zero-configuration, serverless, self-contained; runs reliably on localhost without external dependencies. |
| **HTML5 & CSS3** | User Interface | Semantic structure and custom warm modern bookstore aesthetic without heavy frontend frameworks. |
| **Jinja2** | Template Engine | Built-in context-aware auto-escaping mechanism for secure HTML rendering. |
| **Werkzeug** | Cryptography | Industry-standard password hashing using salted SHA-256 (`generate_password_hash`). |

---

## 6. Database Design & Entity Relationship

The database schema (`database/booknest.db`) consists of six relational tables:

```text
  ┌──────────────┐          ┌──────────────┐
  │    USERS     │          │    BOOKS     │
  ├──────────────┤          ├──────────────┤
  │ id (PK)      │◄───┐     │ id (PK)      │◄───┐
  │ username     │    │     │ seller_id(FK)├───┘
  │ email        │    │     │ title        │
  │ password_hash│    │     │ author       │
  │ full_name    │    │     │ category     │
  │ department   │    │     │ price        │
  └──────────────┘    │     │ condition    │
         ▲            │     └──────────────┘
         │            │            ▲
         │            │            │
  ┌──────┴───────┐    │     ┌──────┴───────┐
  │    ORDERS    │    │     │  ORDER_ITEMS │
  ├──────────────┤    │     ├──────────────┤
  │ id (PK)      │    └────►│ id (PK)      │
  │ user_id (FK) ├─────────►│ order_id (FK)│
  │ order_number │          │ book_id (FK) ├────┘
  │ total_amount │          │ price        │
  │ delivery_loc │          │ quantity     │
  └──────────────┘          └──────────────┘
```

1. **`users`**: Stores student credentials, department, and registration timestamp.
2. **`books`**: Stores textbook title, author, category, price, condition, and foreign key to `users(id)` (seller).
3. **`cart`**: Junction table tracking book IDs and quantities per user session.
4. **`wishlist`**: Stores book bookmarks per user.
5. **`orders`**: Records order number, user ID, total amount, delivery location, and payment mode.
6. **`order_items`**: Line items linked to `orders(id)` and `books(id)`.

---

## 7. Working Workflow
1. **Listing**: Senior student logs in, navigates to `/sell`, enters book details, condition ("Very Good"), and sets price (₹350). The book immediately appears in the catalog.
2. **Browsing & Selection**: Junior student searches for `Java` or `Networks`, adds the textbook to cart, and proceeds to `/checkout`.
3. **Campus Handover**: Student selects a safe meetup point (e.g. *Central Campus Library - Desk 4*) and confirms order.
4. **Receipt Tracking**: Both parties can view the digital receipt under `/orders`.

---

## 8. Ethical Hacking Methodology
The security evaluation followed the standard 7-stage penetration testing lifecycle:

```text
Reconnaissance ──► Enumeration ──► Vulnerability ID ──► Exploitation (PoC)
                                                              │
Secure Retest ◄── Verification ◄── Source Remediation ◄───────┘
```

1. **Reconnaissance**: Reviewing application structure, endpoints, and input parameters.
2. **Enumeration**: Mapping out input routes (`/browse?q=`, `/login`, `/order/<id>`).
3. **Vulnerability Identification**: Analyzing how untrusted data is processed by templates, SQL queries, and authorization handlers.
4. **Controlled Exploitation**: Executing harmless proofs of concept against dummy localhost data.
5. **Source Remediation**: Applying secure coding patterns (parameterized queries, output encoding, ownership verification).
6. **Retesting**: Re-executing identical payloads to prove vulnerability elimination.

---

## 9. Security Findings & Fixes Summary

### Finding 1: Reflected Cross-Site Scripting (Reflected XSS)
- **Vulnerability**: Search parameter `q` reflected unsafely in `browse.html` via `| safe`.
- **Harmless PoC**: `<script>alert("BookNest XSS")</script>`
- **Remediation**: Replaced with Jinja2 default escaping (`{{ search_query }}`).
- **Retest**: Browser displays sanitized text entities: `&lt;script&gt;...` without script execution.

### Finding 2: SQL Injection (SQLi)
- **Vulnerability**: Unsafe string formatting in authentication query.
- **Harmless PoC**: Username: `' OR '1'='1' --` / Password: `anything`
- **Remediation**: Migrated to parameterized queries (`?`) and `check_password_hash`.
- **Retest**: Injection string treated strictly as literal data; rejected with "Invalid credentials".

### Finding 3: Insecure Direct Object Reference (IDOR)
- **Vulnerability**: Route `/order/<order_id>` lacked user ownership verification.
- **Harmless PoC**: Authenticated as User 2 (`student`), accessing User 3's (`rahul`) order `/order/2`.
- **Remediation**: Added server-side ownership check: `if order['user_id'] != session['user_id']: abort(403)`.
- **Retest**: Attempting to view another student's order returns HTTP 403 Forbidden.

---

## 10. Verification & Test Automation
An automated test suite (`test_booknest.py`) executes 18 unit and integration tests covering:
- All 14 page routes (HTTP 200 responses).
- Shopping cart, checkout, seller dashboard, and listing workflows.
- Successful demonstration of all three vulnerabilities in **Demo Mode**.
- Successful verification of all three remediations in **Secure Mode**.

Run tests using:
```powershell
py test_booknest.py
```

---

## 11. Limitations & Future Scope
- **Limitations**: Restricted to localhost testing with mock student data; physical handoffs simulate payments without a real payment gateway.
- **Future Scope**:
  - Integrate CSRF token validation on all POST forms.
  - Implement real-time campus chat between buyer and seller using WebSockets.
  - Add image upload with strict MIME-type validation and server-side virus scanning.

---

## 12. Conclusion
BookNest successfully demonstrates how a genuine, modern web application can be designed, subjected to an authorized ethical hacking assessment, and comprehensively secured. The project showcases both full-stack software development competency and fundamental application security practices.
