# BookNest Ethical Hacking Security Assessment
### Academic Penetration Testing & Vulnerability Remediation Report

---

## 1. Introduction
This security assessment document details the authorized ethical hacking assessment and subsequent remediation performed on **BookNest — College Used-Book Marketplace**. The goal of this academic project is to demonstrate real-world web application vulnerabilities in a controlled local setting, document evidence of exploitation, implement industry-standard security fixes, and retest to prove remediation.

---

## 2. Scope
The scope of this assessment is strictly limited to:
- **Target URL**: `http://127.0.0.1:5000` (Localhost loopback interface)
- **Application**: BookNest Flask Web Application
- **Database**: Local SQLite database (`database/booknest.db`)
- **Data Scope**: Synthetic mock student accounts and sample course textbook listings only.

> [!NOTE]
> Testing was strictly confined to localhost. No external networks, real user credentials, or remote endpoints were accessed or impacted.

---

## 3. Authorization
This assessment was performed as an approved academic exercise for a 15-mark Ethical Hacking coursework requirement. The application and database were developed, hosted, and tested exclusively by the student on a locally controlled development system.

---

## 4. Testing Environment
- **Host Machine**: Windows 11 (Development Workstation)
- **Runtime**: Python 3.14 / Flask 3.1
- **Database**: SQLite 3 (Embedded relational database)
- **Browser**: Chromium-based Browser / Integrated Test Client
- **Testing Tools**: Standard web browser, Python `unittest` / `test_client`, and manual parameter manipulation.

---

## 5. Application Overview
BookNest is a student marketplace enabling university peers to buy, sell, and exchange course textbooks. Core features include:
1. **Catalog & Search**: Real-time keyword filtering across title, author, and academic department.
2. **Authentication System**: Student registration, password hashing, and session management.
3. **Commerce Features**: Wishlist, shopping cart, campus drop-point selection, and order generation.
4. **Seller Management**: Listing used textbooks with condition tags and tracking sold status.

---

## 6. Vulnerability 1 — Reflected Cross-Site Scripting (Reflected XSS)
- **Vulnerability Type**: CWE-79: Improper Neutralization of Input During Web Page Generation
- **Location**: Book Search Functionality (`GET /browse?q=`)
- **Severity**: Medium / Low (Academic Severity: Low)
- **Status**: Vulnerable in Demo Mode -> Fixed & Retested in Secure Mode

### Technical Cause:
The application reflects the user's search query `q` directly in the search feedback banner without escaping dangerous HTML and JavaScript characters. When rendered using the unescaped template filter (`| safe`), the browser interprets user input as executable markup.

---

## 7. XSS Testing Procedure
1. Navigate to the catalog page: `http://127.0.0.1:5000/browse`.
2. Locate the search bar.
3. Input the harmless proof-of-concept payload:
   ```html
   <script>alert("BookNest XSS")</script>
   ```
4. Press Enter or click the Search icon.
5. Inspect the HTTP response and browser behavior.

---

## 8. XSS Evidence
- **Before Fix (`SECURITY_DEMO_MODE = True`)**:
  The application generates the following raw response HTML:
  ```html
  <div class="search-feedback-banner">
    <p>Showing search results for: <strong><script>alert("BookNest XSS")</script></strong></p>
  </div>
  ```
  The browser executes the JavaScript script block and displays a modal alert dialog with the text `"BookNest XSS"`.

- **Automated Test Confirmation**:
  ```text
  [PASS] Reflected XSS Test: Raw unescaped JavaScript payload rendered in response!
  ```

---

## 9. XSS Risk Explanation
In an unpatched production application, Reflected Cross-Site Scripting allows an attacker to craft a malicious URL containing JavaScript. If an authenticated student clicks this link, the attacker's script could:
- Steal the user's active session cookie (`document.cookie`), leading to account takeover.
- Redirect the student to a credential-harvesting phishing page.
- Perform unauthorized actions on behalf of the victim (such as placing fraudulent book orders).

---

## 10. XSS Remediation
- **Fix Applied**: Replace raw unescaped output rendering with context-aware HTML entity encoding. In Flask/Jinja2, removing the `| safe` filter enables automatic HTML escaping:
  ```jinja2
  <!-- SECURE REMEDIATION IN browse.html -->
  <p>Showing search results for: <strong>{{ search_query }}</strong></p>
  ```
- **Escaped Output**:
  Special characters are encoded into safe HTML entities:
  - `<` becomes `&lt;`
  - `>` becomes `&gt;`
  - `"` becomes `&#34;`
  The payload is rendered strictly as harmless text on screen and cannot be executed as code by the browser engine.

---

## 11. Vulnerability 2 — SQL Injection (Authentication Bypass)
- **Vulnerability Type**: CWE-89: Improper Neutralization of Special Elements used in an SQL Command
- **Location**: Student Login Form (`POST /login`)
- **Severity**: High (Academic Severity: Medium)
- **Status**: Vulnerable in Demo Mode -> Fixed & Retested in Secure Mode

### Technical Cause:
The authentication handler constructs SQL queries using raw Python string formatting (`f"SELECT ... WHERE email = '{input}'"`). Untrusted input containing SQL syntax characters (such as `'` and `--`) alters the logical structure of the SQL query.

---

## 12. SQL Injection Testing Procedure
1. Navigate to the login page: `http://127.0.0.1:5000/login`.
2. In the **Email or Username** field, enter the classic authentication bypass payload:
   ```sql
   ' OR '1'='1' --
   ```
3. In the **Password** field, enter any arbitrary string (e.g. `dummy_pass`).
4. Click **Login to BookNest**.
5. Observe the authentication result.

---

## 13. SQL Injection Evidence
- **Before Fix (`SECURITY_DEMO_MODE = True`)**:
  The backend constructs and executes the following raw query:
  ```sql
  SELECT * FROM users WHERE email = '' OR '1'='1' --' AND password_plain = 'dummy_pass'
  ```
  The SQL comment characters (`--`) instruct SQLite to ignore the remainder of the query, including the password check. The condition `'1'='1'` evaluates to true for all rows, returning the first user record (`admin` or `student`) and creating a valid authenticated session.
  The server responds with:
  ```text
  Welcome back, Aarav Sharma!
  ```

- **Automated Test Confirmation**:
  ```text
  [PASS] SQL Injection Login Test: Bypassed password check with payload: ' OR '1'='1' --
  ```

---

## 14. SQL Injection Risk Explanation
SQL injection is one of the most critical vulnerabilities in web applications (OWASP Top 10 #3). Its risks include:
- Complete authentication bypass without knowing user passwords.
- Unauthorized reading of sensitive database tables (user details, order histories, financial records).
- Potential modification or destruction of database records.

---

## 15. SQL Injection Remediation
- **Fix Applied**: Replace string concatenation with **Parameterized Queries** (Prepared Statements) and verify passwords against cryptographically secure one-way hashes using Werkzeug's `check_password_hash`.
  ```python
  # SECURE REMEDIATION IN app.py
  cursor.execute("SELECT * FROM users WHERE email = ? OR username = ?", (username_or_email, username_or_email))
  user = cursor.fetchone()

  if user and check_password_hash(user['password_hash'], password):
      session['user_id'] = user['id']
  ```
  With parameterized queries, SQLite treats the input strictly as literal string data. The characters `'` and `--` have no syntactic effect on the query structure.

---

## 16. Vulnerability 3 — Insecure Direct Object Reference (IDOR / Broken Access Control)
- **Vulnerability Type**: CWE-639: Authorization Bypass Through User-Controlled Key
- **Location**: Order Receipt & Details Route (`GET /order/<order_id>`)
- **Severity**: Medium
- **Status**: Vulnerable in Demo Mode -> Fixed & Retested in Secure Mode

### Technical Cause:
The order details handler verifies that the client is logged in (Authentication), but fails to verify whether the requesting user actually owns the requested order record (Authorization). The application directly queries the database using the user-supplied `order_id` parameter without ownership validation.

---

## 17. IDOR Testing Procedure
1. Log in as student `student@booknest.local` (User ID: 2).
2. Place an order or navigate to **My Orders** (`http://127.0.0.1:5000/orders`).
3. Note that the student's own order is Order #1 (`http://127.0.0.1:5000/order/1`).
4. In the browser address bar, change the URL to:
   ```text
   http://127.0.0.1:5000/order/2
   ```
5. Press Enter and observe the rendered page.

---

## 18. IDOR Evidence
- **Before Fix (`SECURITY_DEMO_MODE = True`)**:
  The application fetches Order #2 from the database and renders it without checking `order.user_id == session['user_id']`. Student A (`Aarav Sharma`) is able to view Student B's (`Rahul Deshmukh`) full order receipt, including book purchases, campus handover spot, and order total.

- **Automated Test Confirmation**:
  ```text
  [PASS] IDOR Access Test: Logged in student accessed Order #2 belonging to Rahul Deshmukh!
  ```

---

## 19. IDOR Risk Explanation
Broken Access Control (OWASP Top 10 #1) occurs when applications do not enforce authorization boundaries between different users. Risks include:
- Unauthorized disclosure of personal information (student names, email addresses, campus pickup points).
- Breach of privacy and order transaction details.
- Potential tampering with another user's orders or listings.

---

## 20. IDOR Remediation
- **Fix Applied**: Implement strict server-side ownership authorization. Before returning order details, the server verifies that the authenticated user's ID matches the order's `user_id`:
  ```python
  # SECURE REMEDIATION IN app.py
  if order['user_id'] != session['user_id']:
      flash("Access Denied: You are not authorized to view this order.", "danger")
      return render_template('orders.html', orders=[]), 403
  ```
  If an unauthorized user attempts to access another user's order ID, the server terminates the request with **HTTP 403 Forbidden**.

---

## 21. Retesting & Verification Summary

All three vulnerabilities were retested with `SECURITY_DEMO_MODE = False`. The results are summarized below:

| Vulnerability | Vulnerable Behavior (Before Fix) | Applied Remediation | Retest Result (After Fix) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. Reflected XSS** (`/browse?q=`) | Injected `<script>` executed in browser | Context-aware Jinja2 HTML output encoding | Payload rendered safely as text entity: `&lt;script&gt;...` | **RESOLVED** |
| **2. SQL Injection** (`/login`) | `' OR '1'='1' --` bypassed authentication | Parameterized SQLite queries (`?`) + Password Hashing | Input treated as literal text; login rejected safely | **RESOLVED** |
| **3. IDOR** (`/order/<id>`) | User 2 viewed User 3's private order receipt | Ownership authorization check (`order.user_id == session.user_id`) | Unauthorized access blocked with HTTP 403 Forbidden | **RESOLVED** |

---

## 22. Additional Security Improvements Implemented
Beyond the three primary vulnerability demonstrations, the following security best practices were established in the codebase:
1. **Cryptographic Password Hashing**: Passwords are saved as one-way PBKDF2/SHA-256 hashes using `werkzeug.security.generate_password_hash`.
2. **Session Security**: Session tokens are cryptographically signed with a secure server secret key.
3. **Foreign Key Constraints**: SQLite foreign key constraints (`PRAGMA foreign_keys = ON`) maintain referential integrity.
4. **Input Type Sanitization**: Strict casting of numeric IDs (`<int:book_id>`, `<int:order_id>`) in Flask route parameters.

---

## 23. Conclusion
The security assessment of BookNest successfully demonstrated three classic web application vulnerabilities (Reflected XSS, SQL Injection, and IDOR) within realistic e-commerce features. Through parameterized queries, output encoding, and authorization validation, all three issues were remediated and verified through retesting. The final application satisfies both functional marketplace requirements and secure coding standards.
