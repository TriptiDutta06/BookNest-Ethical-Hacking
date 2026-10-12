/**
 * CyberVault - Smart Campus Security Portal
 * Client-side script for interactive Security Lab testing, payload injection,
 * and live vulnerability demonstration.
 */

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // 1. Quick Payload Fillers
    // -------------------------------------------------------------
    window.setPayload = function(inputId, payloadText) {
        const inputElement = document.getElementById(inputId);
        if (inputElement) {
            inputElement.value = payloadText;
            inputElement.focus();
            inputElement.classList.add('glow-pulse');
            setTimeout(() => inputElement.classList.remove('glow-pulse'), 800);
        }
    };

    // -------------------------------------------------------------
    // 2. Interactive XSS Demonstration Sandbox
    // -------------------------------------------------------------
    const xssForm = document.getElementById('xss-test-form');
    if (xssForm) {
        xssForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('xss-input');
            const payload = input.value.trim() || "<script>alert('CyberVault XSS Demo')</script>";
            const terminalOutput = document.getElementById('xss-terminal-output');
            const liveRenderArea = document.getElementById('xss-live-render-container');

            terminalOutput.innerHTML = `<span class="text-cyan">[~] Sending payload to /lab/test-xss...</span><br>`;

            try {
                const response = await fetch('/lab/test-xss', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ payload: payload })
                });

                const data = await response.json();

                let log = `<span class="text-dim">[${new Date().toLocaleTimeString()}]</span> `;
                if (!data.is_fixed) {
                    log += `<span class="badge badge-vulnerable">VULNERABLE REFLECTION</span><br>`;
                    log += `<span class="text-red">Payload:</span> <code>${escapeHtml(data.payload)}</code><br>`;
                    log += `<span class="text-amber">Raw Output Reflected into DOM:</span> <code>${escapeHtml(data.rendered_output)}</code><br>`;
                    log += `<span class="text-muted">${data.explanation}</span><br>`;
                    
                    terminalOutput.innerHTML = log;

                    // Controlled safe demonstration in live render container
                    if (liveRenderArea) {
                        liveRenderArea.innerHTML = `
                            <div style="padding: 10px; border: 1px dashed #ff3366; background: rgba(255, 51, 102, 0.1); border-radius: 6px; margin-top: 10px;">
                                <strong class="text-red"><i class="fa fa-bug"></i> Reflected DOM Preview:</strong><br>
                                <div id="xss-render-target"></div>
                            </div>
                        `;
                        const target = document.getElementById('xss-render-target');
                        target.innerHTML = data.rendered_output;
                        
                        // Execute embedded script tags in demonstration if user used <script>
                        const scripts = target.getElementsByTagName('script');
                        for (let s of scripts) {
                            try {
                                eval(s.innerText);
                            } catch (err) {
                                console.warn("XSS demo execution note:", err);
                            }
                        }
                    }
                } else {
                    log += `<span class="badge badge-secure">DEFENSE ACTIVE - ESCAPED</span><br>`;
                    log += `<span class="text-green">Escaped Output:</span> <code>${data.rendered_output}</code><br>`;
                    log += `<span class="text-muted">${data.explanation}</span><br>`;
                    terminalOutput.innerHTML = log;

                    if (liveRenderArea) {
                        liveRenderArea.innerHTML = `
                            <div style="padding: 10px; border: 1px solid #00ff9d; background: rgba(0, 255, 157, 0.1); border-radius: 6px; margin-top: 10px;">
                                <strong class="text-green">&#10004; Safe Escaped Output:</strong><br>
                                <code>${data.rendered_output}</code>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                terminalOutput.innerHTML += `<span class="text-red">[!] Error executing XSS test: ${error.message}</span>`;
            }
        });
    }

    // -------------------------------------------------------------
    // 3. Interactive SQL Injection Demonstration Sandbox
    // -------------------------------------------------------------
    const sqliForm = document.getElementById('sqli-test-form');
    if (sqliForm) {
        sqliForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('sqli-input');
            const usernameInput = input.value.trim();
            const terminalOutput = document.getElementById('sqli-terminal-output');

            terminalOutput.innerHTML = `<span class="text-cyan">[~] Executing query against SQLite user directory...</span><br>`;

            try {
                const response = await fetch('/lab/test-sqli', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username_input: usernameInput })
                });

                const data = await response.json();

                let log = `<span class="text-dim">[${new Date().toLocaleTimeString()}]</span> `;
                if (data.status === 'VULNERABLE') {
                    log += `<span class="badge badge-vulnerable">SQL INJECTION SUCCESSFUL</span><br>`;
                    log += `<span class="text-amber">Raw Executed SQL:</span><br><code style="color:#00f0ff;">${escapeHtml(data.executed_query)}</code><br><br>`;
                    log += `<span class="text-red">Records Leaked (${data.records_found}):</span><br>`;
                    log += `<pre style="background:#040711; padding:8px; border-radius:6px; overflow-x:auto;">${JSON.stringify(data.data, null, 2)}</pre>`;
                    log += `<p class="text-muted mt-1">${data.explanation}</p>`;
                } else if (data.status === 'SECURE') {
                    log += `<span class="badge badge-secure">PREPARED STATEMENT ENFORCED</span><br>`;
                    log += `<span class="text-green">Parameterized Query:</span><br><code style="color:#00ff9d;">${escapeHtml(data.executed_query)}</code><br><br>`;
                    log += `<span class="text-muted">Records Matched: ${data.records_found}</span><br>`;
                    if (data.records_found > 0) {
                        log += `<pre style="background:#040711; padding:8px; border-radius:6px;">${JSON.stringify(data.data, null, 2)}</pre>`;
                    } else {
                        log += `<span class="text-dim">No records matched literal username "${escapeHtml(usernameInput)}". Query logic intact!</span><br>`;
                    }
                    log += `<p class="text-muted mt-1">${data.explanation}</p>`;
                } else {
                    log += `<span class="badge badge-critical">QUERY ERROR</span><br>`;
                    log += `<span class="text-red">${escapeHtml(data.error || 'Syntax error in SQL input')}</span><br>`;
                    log += `<code style="color:#f59e0b;">${escapeHtml(data.executed_query)}</code>`;
                }

                terminalOutput.innerHTML = log;
            } catch (error) {
                terminalOutput.innerHTML += `<span class="text-red">[!] Error executing SQL test: ${error.message}</span>`;
            }
        });
    }

    // -------------------------------------------------------------
    // 4. Interactive Weak Authentication Sandbox
    // -------------------------------------------------------------
    const authForm = document.getElementById('auth-test-form');
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const passwordInput = document.getElementById('auth-password-input').value;
            const terminalOutput = document.getElementById('auth-terminal-output');

            terminalOutput.innerHTML = `<span class="text-cyan">[~] Testing authentication attempt against admin account...</span><br>`;

            try {
                const response = await fetch('/lab/test-auth', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: 'admin', password: passwordInput })
                });

                const data = await response.json();

                let log = `<span class="text-dim">[${new Date().toLocaleTimeString()}]</span> `;
                if (!data.is_fixed) {
                    log += `<span class="badge badge-vulnerable">VULNERABLE (UNTHROTTLED)</span><br>`;
                    log += `<span class="${data.authenticated ? 'text-green' : 'text-red'}">${data.message}</span><br>`;
                    log += `<span class="text-muted">Account lockout: DISABLED. Unlimited brute-force attempts possible.</span>`;
                } else {
                    if (data.is_locked) {
                        log += `<span class="badge badge-critical">ACCOUNT LOCKED OUT</span><br>`;
                        log += `<span class="text-red"><strong>${data.message}</strong></span><br>`;
                        log += `<span class="text-muted">Brute-force protection successfully engaged after 5 failed attempts.</span>`;
                    } else if (data.authenticated) {
                        log += `<span class="badge badge-secure">AUTHENTICATED</span><br>`;
                        log += `<span class="text-green">${data.message}</span><br>`;
                    } else {
                        log += `<span class="badge badge-medium">ATTEMPT RECORDED</span><br>`;
                        log += `<span class="text-amber">${data.message}</span><br>`;
                        log += `<span class="text-muted">Failed counter: ${data.failed_attempts} / 5</span>`;
                    }
                }

                terminalOutput.innerHTML = log;
            } catch (error) {
                terminalOutput.innerHTML += `<span class="text-red">[!] Error executing Auth test: ${error.message}</span>`;
            }
        });
    }

    // Helper: HTML escaper for safe log rendering
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
