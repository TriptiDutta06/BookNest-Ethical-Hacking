# CYBERVAULT: SMART CAMPUS SECURITY PORTAL
## ACADEMIC PROJECT REPORT (15 MARKS)
**Course:** Ethical Hacking & Cyber Defense  
**Platform:** Python (Flask) / SQLite3 / Localhost (127.0.0.1:5000)

---

### 1. Title
**CyberVault — Smart Campus Security Portal: Design, Vulnerability Assessment, and Remediation on Localhost Infrastructure**

---

### 2. Abstract
Web applications hosted across university networks manage high volumes of academic credentials, research data, and incident logs. However, insecure programming practices often introduce vulnerabilities like Cross-Site Scripting (XSS), SQL Injection (SQLi), and weak credential defenses. This project presents **CyberVault**, a fictional smart campus security portal developed to demonstrate the complete six-stage ethical hacking lifecycle: *Web Application Development, Vulnerability Identification, Controlled Local Exploitation, Evidence Collection, Security Remediation, and Retesting*. Running strictly on `http://127.0.0.1:5000`, the platform intentionally incorporates three controlled, low-risk vulnerabilities for educational audit. By demonstrating parameterization, context-aware escaping, and rate-limiting lockout controls, the system dynamically recalculates a campus security posture score from **72/100 (Vulnerable)** to **96/100 (Hardened)**.

---

### 3. Introduction
Modern educational institutions operate distributed intranet portals for campus incident reporting, facility management, and student services. Because these applications are often developed rapidly without comprehensive security audits, they are prone to common OWASP Top 10 vulnerabilities. Ethical hacking serves as an essential methodology to identify, exploit in a controlled manner, and remediate these vulnerabilities before malicious adversaries can exploit them. CyberVault bridges theoretical cybersecurity concepts with practical hands-on application development.

---

### 4. Problem Statement
Academic portals frequently fail to validate and sanitize user inputs, exposing databases and clients to dangerous attack vectors:
1. Search queries are directly concatenated into HTML pages, allowing Reflected Cross-Site Scripting.
2. User authentication queries are constructed with string interpolation, allowing SQL Injection bypasses.
3. Administrative gateways lack brute-force defense mechanisms, permitting automated dictionary attacks.

---

### 5. Objectives
1. Build an attractive, realistic Security Operations Center (SOC) web application using Python (Flask) and SQLite.
2. Embed three controlled, low-risk vulnerabilities restricted strictly to localhost.
3. Demonstrate controlled exploitation using non-destructive payloads.
4. Implement secure software engineering practices (Prepared Statements, HTML escaping, Account lockout).
5. Provide live evidence and retesting capabilities to prove vulnerability remediation and score improvement.

---

### 6. Scope
- **Included:** Fictional campus incident logging, local SQLite user database, controlled Reflected XSS sandbox, safe SQL injection query analyzer, brute-force lockout simulation, dynamic security score counter.
- **Excluded:** External attacks, network scanning, DDoS, cookie hijacking, or destructive database operations (DROP/DELETE).

---

### 7. Technologies Used
- **Backend Framework:** Python 3 + Flask (Lightweight, readable WSGI framework)
- **Database Management:** SQLite 3 (Serverless, zero-configuration local database)
- **Frontend Presentation:** HTML5, Modern CSS3 (Dark Cyberpunk SOC Theme, Neon Glassmorphism)
- **Client Logic:** Vanilla JavaScript (Fetch API, DOM manipulation)
- **Deployment Endpoint:** `http://127.0.0.1:5000` (Localhost ONLY)

---

### 8. System Requirements
- **Hardware:** Intel Core i3 or higher / AMD equivalent, 4GB RAM minimum, 200MB free disk space.
- **Software:** Windows 10/11, Python 3.8+, Modern web browser (Chrome/Edge/Firefox), VS Code.

---

### 9. System Architecture
```
+--------------------------------------------------------------------+
|                         CLIENT BROWSER                             |
|               (Dark Cyber SOC UI / 127.0.0.1:5000)                 |
+--------------------------------------------------------------------+
                 ▲                                   │
      HTTP HTML / JSON Response               HTTP POST / GET
                 │                                   ▼
+--------------------------------------------------------------------+
|                       FLASK APPLICATION LAYER                      |
|  - Routing Engine (/login, /dashboard, /incidents, /security-lab)  |
|  - Vulnerability Toggle Switches (Vulnerable vs Patched Mode)       |
|  - Input Validation & Escaping Engine (html.escape)               |
+--------------------------------------------------------------------+
                 ▲                                   │
           Row Factory Data                  Parameterized / Raw SQL
                 │                                   ▼
+--------------------------------------------------------------------+
|                         SQLITE DATABASE                            |
|      Tables: users | incidents | security_settings                 |
+--------------------------------------------------------------------+
```

---

### 10. Modules
1. **Landing Module (`index.html`):** Portal overview, mission statement, threat detection overview, and security rating.
2. **Authentication Gateway (`login.html`):** Role-based access for Security Officers with pre-configured demo account indicators.
3. **SOC Operations Dashboard (`dashboard.html`):** Real-time telemetry, vulnerability matrix, incident statistics, and recent activity cards.
4. **Threat Incident Reporter (`report.html`):** Multi-severity campus incident logger writing to SQLite.
5. **Incident Registry & Search (`incidents.html`):** Search filter and incident review module, acting as the primary reflected input vector.
6. **Security Testing Lab (`security_lab.html`):** Educational vulnerability testing sandbox featuring side-by-side exploitation and defense retesting.

---

### 11. Ethical Hacking Methodology
The project strictly implements the standard six-stage ethical hacking assessment methodology:
1. **Reconnaissance & Footprinting:** Examining application routes, parameters, and form fields.
2. **Vulnerability Identification:** Locating unsanitized inputs in search parameters and database queries.
3. **Controlled Exploitation:** Submitting benign proof-of-concept payloads (`<script>alert()</script>`, `' OR '1'='1`).
4. **Evidence Collection:** Capturing popups, database table outputs, and authorization bypasses.
5. **Security Remediation:** Implementing input escaping, parameterized queries, and lockout thresholds.
6. **Verification & Retesting:** Re-running the identical exploit strings to verify defense efficacy.

---

### 12. Vulnerabilities Studied
| Vulnerability | OWASP Top 10 | Severity | Root Cause |
|---|---|---|---|
| **Reflected XSS** | A03:2021 - Injection | Low | Trusting user input in search query without HTML entity escaping. |
| **SQL Injection** | A03:2021 - Injection | Medium | String concatenation inside SQL commands rather than prepared statements. |
| **Weak Authentication** | A07:2021 - Identification & Auth Failures | Low | Absence of rate-limiting, allowing indefinite brute-force attempts. |

---

### 13. Vulnerability Demonstration & Evidence
1. **Reflected XSS:**
   - *Payload:* `<script>alert('CyberVault XSS Demo')</script>`
   - *Observation:* The JavaScript alert executes on the client machine, proving script injection into the browser DOM.
2. **SQL Injection:**
   - *Payload:* `' OR '1'='1`
   - *Observation:* The `WHERE username = '' OR '1'='1'` clause forces SQLite to return all registered users, bypassing username matching.
3. **Weak Authentication:**
   - *Simulation:* Submitting repeated failed password guesses against `admin`.
   - *Observation:* In vulnerable mode, unlimited attempts are allowed with no delay or penalty.

---

### 14. Security Measures (Remediation)
1. **XSS Defense:** Enforced context-aware HTML entity encoding using `html.escape()` and Jinja2 default escaping. Characters like `<` and `>` become `&lt;` and `&gt;`.
2. **SQLi Defense:** Migrated from string concatenation `f"SELECT ... '{input}'"` to parameterized SQL queries `cursor.execute("SELECT ... WHERE username = ?", (input,))`.
3. **Auth Defense:** Implemented a database-backed failed attempt counter. Upon reaching 5 consecutive failures, `is_locked` is flagged as `1`, locking the account.

---

### 15. Testing & Validation Matrix
| Test Case | Vulnerability | Input Payload | Result (Before Fix) | Result (After Fix) |
|---|---|---|---|---|
| TC-01 | Reflected XSS | `<script>alert('CyberVault XSS Demo')</script>` | Popup dialog appears in browser. | Payload rendered as literal text string. |
| TC-02 | SQL Injection | `' OR '1'='1` | Full user directory leaked (2 records). | Zero records matched; query logic preserved. |
| TC-03 | Weak Auth | 5 consecutive wrong passwords | Unlimited guesses allowed. | Account locked out; brute-force halted. |

---

### 16. Results & Security Score Comparison
- **Vulnerable Baseline Score:** **72 / 100** (Grade C — High Risk)
- **Post-Remediation Score:** **96 / 100** (+8 XSS, +10 SQLi, +6 Auth) (Grade A — Hardened)

---

### 17. Advantages
- Beginner-friendly architecture: clear Python and Flask code without convoluted framework bloat.
- Safe, non-destructive educational sandboxing restricted to localhost.
- Real-time interactive dashboard providing visual before-and-after proof.

---

### 18. Limitations
- Runs exclusively on a single-node SQLite instance suitable for academic demonstration.
- Does not implement enterprise distributed Redis session stores or cryptographic HSMs.

---

### 19. Future Scope
- Incorporate multi-factor authentication (TOTP QR codes).
- Add CSRF (Cross-Site Request Forgery) protection tokens with Flask-WTF.
- Implement automated audit log export into SIEM-compatible CEF/JSON format.

---

### 20. Conclusion
CyberVault demonstrates that cybersecurity is an active, iterative discipline. By coupling a polished campus security interface with transparent, safe vulnerability demonstrations, the project successfully fulfills the academic requirements of a 15-mark ethical hacking curriculum.
