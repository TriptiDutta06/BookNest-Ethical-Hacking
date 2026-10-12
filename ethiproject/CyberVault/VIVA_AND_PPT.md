# CYBERVAULT — PRESENTATION (PPT) & VIVA VOCE PREPARATION GUIDE
### Smart Campus Security Portal (15-Mark Ethical Hacking Project)

---

# PART A: 12-SLIDE PRESENTATION STRUCTURE (PPT)

### Slide 1: Title Slide
- **Title:** CyberVault – Smart Campus Security Portal
- **Subtitle:** Web Vulnerability Identification, Controlled Exploitation & Remediation on Localhost
- **Student Name & Roll No:** [Your Name / Roll Number]
- **Department:** Computer Science & Engineering / Information Technology
- **Guide / Evaluator:** [Professor Name]

---

### Slide 2: Problem Statement
- Campus portals handle sensitive student and faculty records.
- Common development oversights introduce critical OWASP vulnerabilities.
- Absence of input sanitization leads to Cross-Site Scripting (XSS).
- Unparameterized SQL queries expose database contents.
- Lack of authentication rate-limiting enables automated dictionary attacks.

---

### Slide 3: Project Objectives
- Build a realistic Security Operations Center (SOC) web portal.
- Implement the 6-stage **Ethical Hacking Lifecycle**.
- Embed three safe, controlled vulnerabilities strictly on `127.0.0.1`.
- Demonstrate live before-and-after exploit mitigation.
- Quantify application resilience with a dynamic **Security Posture Score** (72 ➔ 96 / 100).

---

### Slide 4: Application Overview & Features
- **Modern Cyber Theme:** Dark mode, glassmorphism, neon status badges.
- **Incident Management:** Phishing, Malware, and Suspicious Login triage.
- **Security Testing Lab:** Dedicated sandbox for real-time vulnerability retesting.
- **Role-Based Auth:** Campus Security Officer access with pre-configured demo account.

---

### Slide 5: System Architecture & Technology
- **Backend:** Python 3 + Flask (Microframework)
- **Database:** SQLite 3 (Auto-seeded with campus telemetry data)
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API for AJAX test sandboxes)
- **Environment:** Strictly bound to `http://127.0.0.1:5000` (Localhost)

---

### Slide 6: Ethical Hacking Lifecycle
1. **Web Application:** Functional campus security portal.
2. **Identification:** Discovering unvalidated input fields.
3. **Exploitation:** Executing benign proof-of-concept payloads.
4. **Evidence:** Capturing alert boxes and query disclosures.
5. **Security Fix:** Escaping inputs, parameterized queries, and account lockout.
6. **Retesting:** Verifying neutralization and posture elevation.

---

### Slide 7: Vulnerability 1 — Reflected XSS
- **Concept:** User search input reflected directly into HTML DOM without encoding.
- **Payload:** `<script>alert('CyberVault XSS Demo')</script>`
- **Before Fix:** Script executes inside victim browser.
- **Remediation:** Context-aware HTML entity escaping using `html.escape()`.
- **After Fix:** Tags rendered as inert text (`&lt;script&gt;`).

---

### Slide 8: Vulnerability 2 — SQL Injection (SQLi)
- **Concept:** String concatenation in SQL command string.
- **Payload:** `' OR '1'='1`
- **Before Fix:** Condition evaluates to TRUE, dumping user directory without authentication.
- **Remediation:** Parameterized queries (Prepared Statements with `?`).
- **After Fix:** Payload treated strictly as literal string data; query returns zero leaks.

---

### Slide 9: Vulnerability 3 — Weak Authentication
- **Concept:** No rate-limiting or attempt restrictions on administrative login.
- **Attack Vector:** Automated brute-force / password spraying.
- **Remediation:** Threshold counter in SQLite; temporary account lockout triggered at **5 consecutive failed attempts**.
- **Evidence:** System raises a high-priority lockout alert; login access is frozen.

---

### Slide 10: Security Fixes & Defensive Coding
- **Output Encoding:** Neutralizes malicious characters before browser parsing.
- **Parameterized SQL:** Separates SQL syntax from user-supplied data at the database engine level.
- **Account Lockout:** Thwarts dictionary attacks and enforces access governance.

---

### Slide 11: Results & Security Score Progression
- **Baseline Vulnerable Score:** `72 / 100` (All 3 vulnerabilities active)
- **XSS Patch:** `+8 Points`
- **SQL Injection Patch:** `+10 Points`
- **Authentication Lockout Patch:** `+6 Points`
- **Final Hardened Posture Score:** `96 / 100` (Grade A Resilience)

---

### Slide 12: Conclusion & Future Scope
- **Conclusion:** Proved that secure coding principles effectively neutralize OWASP Top 10 vulnerabilities without complex infrastructure overhead.
- **Future Enhancements:**
  - Multi-Factor Authentication (MFA / TOTP).
  - CSRF Token verification across all POST forms.
  - Automated intrusion alerts exported to external SIEM tools.

---
---

# PART B: VIVA VOCE QUESTIONS & ANSWERS (EASY TO SPEAK)

#### Q1: What is ethical hacking?
> **Answer:** Ethical hacking is the authorized practice of inspecting and testing computer systems or web applications to discover security vulnerabilities so they can be fixed before malicious hackers exploit them.

#### Q2: What is a vulnerability?
> **Answer:** A vulnerability is a flaw, bug, or weakness in a system's design, code, or configuration that can be exploited by an attacker to compromise confidentiality, integrity, or availability.

#### Q3: What is the difference between a vulnerability and an exploit?
> **Answer:** A vulnerability is the *security hole* or weakness in the software, while an exploit is the *method, script, or payload* used to take advantage of that weakness.

#### Q4: What is Cross-Site Scripting (XSS)?
> **Answer:** XSS is a vulnerability where an attacker injects malicious client-side script into a web application, and the application serves that script back to other users' browsers without proper sanitization.

#### Q5: What is Reflected XSS specifically?
> **Answer:** Reflected XSS happens when user input from an HTTP request (like a search query parameter) is immediately reflected back in the HTTP response without being saved in the database.

#### Q6: How did you fix Reflected XSS in CyberVault?
> **Answer:** By using context-aware HTML entity escaping (`html.escape()` and Jinja2 autoescaping), which converts dangerous characters like `<` and `>` into harmless text entities like `&lt;` and `&gt;`.

#### Q7: What is SQL Injection?
> **Answer:** SQL Injection is a vulnerability where untrusted user input is directly concatenated into a database SQL query, allowing an attacker to manipulate the query structure and access unauthorized data.

#### Q8: How did the `' OR '1'='1` payload work in your project?
> **Answer:** The single quote closed the programmer's username string, and `OR '1'='1'` made the WHERE clause always evaluate to TRUE for every row, forcing SQLite to return all user records.

#### Q9: What are parameterized queries (Prepared Statements)?
> **Answer:** Parameterized queries send the SQL command structure and the user data separately to the database engine. The database treats the input strictly as literal values, never as executable SQL code.

#### Q10: How did you fix SQL Injection in CyberVault?
> **Answer:** We replaced string concatenation with parameterized queries using SQLite's `?` placeholder: `cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))`.

#### Q11: What is authentication vs authorization?
> **Answer:** Authentication verifies **who you are** (e.g. username and password), while authorization determines **what you are allowed to do** (e.g. student vs security officer permissions).

#### Q12: What is brute-force attack?
> **Answer:** A brute-force attack is an automated trial-and-error method where an attacker systematically submits many passwords or passphrases until the correct one is guessed.

#### Q13: How did you mitigate weak authentication and brute-force attacks?
> **Answer:** By implementing a failed-attempt counter in SQLite that automatically triggers an account lockout after 5 consecutive incorrect login attempts.

#### Q14: What is the ethical hacking lifecycle?
> **Answer:** The six stages demonstrated in this project: Web Application ➔ Vulnerability Identification ➔ Controlled Local Exploitation ➔ Evidence Collection ➔ Security Fix ➔ Retesting.

#### Q15: Why did you restrict testing strictly to localhost (127.0.0.1)?
> **Answer:** Because ethical hacking requires explicit authorization. Testing exclusively on localhost guarantees that no external networks, servers, or third-party systems are affected.

#### Q16: What is localhost?
> **Answer:** Localhost refers to the local computing machine currently in use. In IPv4 networking, its loopback IP address is `127.0.0.1`.

#### Q17: Why did you choose Python and Flask for this project?
> **Answer:** Python is readable and beginner-friendly, and Flask is a lightweight microframework that makes routing, session handling, and database interaction clear without heavy boilerplate.

#### Q18: Why did you choose SQLite?
> **Answer:** SQLite is a serverless, zero-configuration, file-based database that runs locally without needing external database servers like MySQL or MongoDB, making it perfect for academic demonstration.

#### Q19: What is input validation?
> **Answer:** Input validation is the process of testing user input against defined rules (such as type, length, format, and permitted characters) before accepting and processing it.

#### Q20: What was the most serious vulnerability in your project and why?
> **Answer:** SQL Injection, because it directly threatens the database backend, potentially allowing unauthorized data leakage or authentication bypass.

#### Q21: How did you verify that your security fixes actually worked?
> **Answer:** By running the exact same exploit payloads after applying the patches and verifying that the XSS script rendered as inert text, the SQLi query returned zero leaked records, and the brute-force lockout blocked repeated guesses.

#### Q22: How does the Security Score work in CyberVault?
> **Answer:** It starts at a baseline of 72/100 when vulnerabilities exist. Fixing XSS awards +8 points, fixing SQL Injection awards +10 points, and fixing Weak Auth awards +6 points, achieving a hardened score of 96/100.
