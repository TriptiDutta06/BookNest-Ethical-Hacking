# BookNest — Ethical Hacking Viva Voce Q&A Guide
### 28 Essential Questions & Natural Student Answers

---

### Q1: What is the main idea of your project?
**Answer:**  
"BookNest is an authentic college used-book marketplace where students can buy, sell, and exchange textbooks on campus. I built this full web application and then conducted an authorized security assessment on it to find, exploit, and fix three common vulnerabilities: Reflected XSS, SQL Injection, and IDOR."

---

### Q2: What is Ethical Hacking?
**Answer:**  
"Ethical hacking is the authorized practice of testing a computer system, network, or web application for security weaknesses, with permission, in order to identify vulnerabilities and fix them before malicious hackers can exploit them."

---

### Q3: What is a vulnerability, an exploit, and a risk?
**Answer:**  
- **Vulnerability**: A flaw or weakness in code or system design (e.g., missing input validation).
- **Exploit**: A piece of software, payload, or technique used to take advantage of that vulnerability.
- **Risk**: The potential loss or impact caused if that vulnerability is successfully exploited.

---

### Q4: Why did you choose Python and Flask for this project?
**Answer:**  
"Flask is a lightweight, clean Python micro-framework. It allows full control over HTTP request handling, session management, and template rendering without unnecessary hidden magic. This makes it ideal for understanding and demonstrating both vulnerable and secure code patterns."

---

### Q5: Why did you use SQLite instead of MySQL or MongoDB?
**Answer:**  
"SQLite is serverless, zero-configuration, and self-contained within a single file (`booknest.db`). It runs reliably on any computer without needing external database servers like XAMPP or Docker, making the project portable and easy to demonstrate."

---

### Q6: Why did you restrict all testing strictly to localhost (127.0.0.1)?
**Answer:**  
"In ethical hacking, strict authorization and scope are paramount. Testing on localhost ensures that all security activities remain contained within my personal machine without impacting any external networks, real user data, or live third-party services."

---

### Q7: What is Reflected XSS (Cross-Site Scripting)?
**Answer:**  
"Reflected XSS occurs when an application receives untrusted data in an HTTP request (such as a search parameter) and immediately reflects it back in the HTTP response page without proper validation or output encoding."

---

### Q8: Where does Reflected XSS occur in BookNest?
**Answer:**  
"In the catalog book search feature at `/browse?q=`. In demo mode, whatever search term the user enters is rendered directly in the search feedback banner without escaping."

---

### Q9: What proof-of-concept payload did you use for XSS?
**Answer:**  
"I used the harmless JavaScript payload `<script>alert("BookNest XSS")</script>`. It proves that user input can be executed as code in the victim's browser without causing any harm."

---

### Q10: How did you fix the Reflected XSS vulnerability?
**Answer:**  
"By applying context-aware HTML entity encoding. In Jinja2, removing the `| safe` filter enables automatic output escaping. Special characters like `<` and `>` are converted to `&lt;` and `&gt;`, so the browser displays the payload as harmless text instead of executing it."

---

### Q11: What is SQL Injection (SQLi)?
**Answer:**  
"SQL Injection occurs when untrusted user input is directly concatenated into a dynamic database query string, allowing an attacker to manipulate the query's logic and structure."

---

### Q12: Why is SQL Injection dangerous?
**Answer:**  
"An attacker can bypass authentication, view private records, modify or delete entire tables, and in severe cases, execute administrative commands on the underlying database server."

---

### Q13: Where did you demonstrate SQL Injection in BookNest?
**Answer:**  
"In the student login form (`/login`). In demo mode, the username or email was concatenated directly into the SQL query string."

---

### Q14: What payload was used to bypass the login, and how does it work?
**Answer:**  
"I used `' OR '1'='1' --`. The single quote closes the string, `'1'='1'` makes the query condition always true, and the double dash `--` comments out the rest of the query, including the password check. This logs in as the first user in the table without needing their password."

---

### Q15: What is a Parameterized Query, and how does it fix SQL Injection?
**Answer:**  
"A parameterized query (prepared statement) uses placeholders (like `?` in SQLite) to separate SQL code from user data. The database engine compiles the query structure first, and user input is treated strictly as literal values. Input characters like quotes or dashes cannot alter the query logic."

---

### Q16: What is the difference between Authentication and Authorization?
**Answer:**  
- **Authentication** answers *'Who are you?'* (e.g., verifying student username and password).
- **Authorization** answers *'What are you permitted to do?'* (e.g., verifying whether a logged-in student has permission to view a specific order).

---

### Q17: What is IDOR (Insecure Direct Object Reference)?
**Answer:**  
"IDOR is a broken access control vulnerability where an application uses user-supplied input (like an ID in the URL) to access a database object directly without verifying whether the requesting user actually owns or is authorized to access that object."

---

### Q18: Where did you demonstrate IDOR in BookNest?
**Answer:**  
"In the order details receipt route at `/order/<order_id>`. When User A (`student`, ID 2) views their own order `/order/1`, changing the URL to `/order/2` allows them to view User B's (`rahul`) private order receipt."

---

### Q19: How did you fix the IDOR vulnerability?
**Answer:**  
"By implementing a server-side ownership authorization check before rendering the order:
`if order['user_id'] != session['user_id']: abort(403)`.
If a student tries to access an order belonging to another user, access is blocked with HTTP 403 Forbidden."

---

### Q20: What is password hashing, and why is plain text storage dangerous?
**Answer:**  
"Password hashing uses a one-way cryptographic mathematical function to convert passwords into an irreversible hash string. Plain text storage is dangerous because if the database is breached, all user passwords are immediately exposed."

---

### Q21: What library did you use for password security?
**Answer:**  
"I used the `werkzeug.security` module, specifically `generate_password_hash` to hash passwords with salt during registration, and `check_password_hash` to securely verify entered passwords during login."

---

### Q22: What is a session, and how does Flask handle it?
**Answer:**  
"A session stores user state across multiple HTTP requests after login. Flask stores session data in a cryptographically signed client-side cookie using the server's `secret_key`, preventing users from tampering with their session identity."

---

### Q23: What does the `SECURITY_DEMO_MODE` switch in `app.py` do?
**Answer:**  
"It is an educational configuration toggle:
- When set to `True`, the application demonstrates the three intentional vulnerabilities for testing.
- When set to `False`, the application activates all secure remediations: parameterized queries, Jinja2 output escaping, and ownership authorization checks."

---

### Q24: What is Vulnerability Remediation?
**Answer:**  
"Remediation is the process of patching or fixing identified security weaknesses by rewriting code, applying security controls, or configuring defenses to prevent exploitation."

---

### Q25: Why is Retesting important after applying a fix?
**Answer:**  
"Retesting verifies that the security fix was implemented correctly, that the vulnerability can no longer be exploited, and that the fix did not break normal application functionality."

---

### Q26: Why did you use dummy/mock data for testing?
**Answer:**  
"To comply with ethical hacking standards and data privacy principles. Using synthetic student names and demo book listings prevents exposure of real personal data during testing."

---

### Q27: How does your UI ensure it doesn't look like a hacking simulator?
**Answer:**  
"BookNest looks like a real student marketplace startup with a warm modern bookstore theme, book cover placeholders, department filters, cart, and campus meetup points. There are no hacker banners, terminal styling, or 'attack' buttons on the customer interface. All security testing is conducted through normal input fields."

---

### Q28: What are the key takeaways from your project?
**Answer:**  
"1. Web applications must never trust user input.  
2. Authentication alone is not enough; authorization checks must protect individual resources.  
3. Secure coding practices like parameterized queries and context-aware output encoding prevent the vast majority of common web attacks."
