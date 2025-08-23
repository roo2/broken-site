# "broken-site" diagnostic assistant project plan

* **Responses API (recommended runtime)**

  * The modern entry point for agents/tools, streaming, structured output, and tool calls. Use it as the “brain” that decides which checker to run, aggregates findings, and formats results. ([OpenAI Platform][1])

# How the model calls your checkers

* **Function Calling (aka “tools”)**

  * Expose your own checkers (DNS lookup, TLS expiry, HTTP GET/HEAD, traceroute, WHOIS, HSTS check, etc.) as JSON-schema tools. The model will pick and call them, you run the code, then feed results back for reasoning. Supports **parallel tool calls** for speed. ([OpenAI Platform][2])

* **Structured Outputs**

  * Enforce a strict JSON schema for your final diagnostic report (e.g., `issues[]` with `severity`, `evidence`, `fix`). This keeps results machine-readable for your UI or API. ([OpenAI Platform][3])

# Built-in hosted tools you might add

These run “next to” the model and can reduce custom plumbing:

* **Web Search (hosted tool)**

  * Let the agent confirm widespread outages, registrar status notices, or recently reported CA incidents. (Useful to correlate a site’s failure with active incidents.) ([OpenAI Platform][4])

* **File Search (hosted retrieval)**

  * Upload server logs, nginx/Apache vhost snippets, or prior audit PDFs and let the agent reference them while diagnosing. ([OpenAI Platform][5])

* **Code Interpreter (hosted Python sandbox)**

  * Handy for analyzing HAR files, curl traces, SSL scan outputs (JSON/CSV), generating graphs of uptime/error spikes, or validating regexes for log triage—without you hosting a Python runner. ([OpenAI Platform][6])

* **Computer Use (hosted browser automation)**

  * For “human-like” checks: open the page, capture a screenshot, read the browser console, follow redirects, and confirm mixed-content or CSP breakage. It’s available via Responses API with a dedicated model. (Note: costs & guardrails apply.) ([OpenAI Platform][7])

# Orchestration & project structure

* **“Using tools” guides**

  * High-level guidance on combining hosted tools, remote MCP servers, and your own function tools. ([OpenAI Platform][8])
* **Agents SDK (optional, nice for multi-tool workflows & tracing)**

  * JS/Python SDKs that formalize tool registration (hosted tools, function tools), inter-agent calling, and tracing—useful as your app grows. ([OpenAI GitHub][9])
* **Streaming**

  * Show live progress (“Checking DNS… SSL… HTTP…”) using server-sent events from the Responses API. ([OpenAI Platform][10])

# Suggested tool design (your custom functions)

Define these as function tools for speed & determinism; the model will call them with parameters:

1. `dns_lookup(domain, record_types[])` → A/AAAA/CNAME/MX/NS/TXT, with TTL & auth NS
2. `whois(domain)` → registrar, expiry, status codes (clientHold/serverHold), name servers
3. `tls_probe(host, port=443, sni=true)` → expiry date, chain, issuer, SANs, OCSP/CRL status, TLS versions, HSTS
4. `http_check(url, method="GET", follow_redirects=true, timeout_sec=10)` → status, redirect chain, headers, body hash/size, core web vitals endpoint pings
5. `security_headers(url)` → HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
6. `mixed_content_scan(url)` → list insecure subresources
7. `tcp_traceroute(host, port)` → network path indicators
8. `dns_health(domain)` → glue/NS alignment, DS/DNSSEC presence, lame delegations
9. `cdn_check(host)` → common CDN/header fingerprints
10. `email_auth_check(domain)` → SPF/DKIM/DMARC presence (handy when diagnosing domain-wide misconfigurations)

Then add a **report schema** (Structured Outputs):
`{ "summary": string, "issues": [ { "id": string, "category": "DNS"|"TLS"|"HTTP"|"SecurityHeaders"|"Content"|"Network", "severity": "info"|"low"|"medium"|"high", "evidence": string, "recommended_fix": string } ], "artifacts": { "screenshots": string[], "raw_samples": { ... } } }` ([OpenAI Platform][3])

# Example flow (Responses API)

1. Send the user prompt (“Diagnose stage.example.com”) + register tools above.
2. Model calls `dns_lookup` and `http_check` in **parallel**; you execute and return results. ([OpenAI Platform][11])
3. Model optionally invokes **Computer Use** to open the page and capture a screenshot/console. ([OpenAI Platform][7])
4. Model compiles a **structured report** and streams it back. ([OpenAI Platform][3])

---

If you want, I can sketch the JSON tool specs and a minimal Node/Python skeleton using the **Responses API** + a couple of the checkers (DNS + TLS) wired up for an MVP.

[1]: https://platform.openai.com/docs/api-reference/responses?utm_source=chatgpt.com "OpenAI Platform"
[2]: https://platform.openai.com/docs/guides/function-calling?utm_source=chatgpt.com "Function calling - OpenAI API"
[3]: https://platform.openai.com/docs/guides/structured-outputs?utm_source=chatgpt.com "Structured model outputs - OpenAI API"
[4]: https://platform.openai.com/docs/guides/tools-web-search?utm_source=chatgpt.com "Web search - OpenAI API"
[5]: https://platform.openai.com/docs/guides/tools-file-search?utm_source=chatgpt.com "File search - OpenAI API"
[6]: https://platform.openai.com/docs/guides/tools-code-interpreter?utm_source=chatgpt.com "Code Interpreter - OpenAI API"
[7]: https://platform.openai.com/docs/guides/tools-computer-use?utm_source=chatgpt.com "Computer use - OpenAI API"
[8]: https://platform.openai.com/docs/guides/tools?utm_source=chatgpt.com "Using tools - OpenAI API"
[9]: https://openai.github.io/openai-agents-js/guides/tools/?utm_source=chatgpt.com "Tools | OpenAI Agents SDK"
[10]: https://platform.openai.com/docs/guides/streaming-responses?utm_source=chatgpt.com "Streaming API responses - OpenAI API"
[11]: https://platform.openai.com/docs/guides/function-calling/parallel-function-calling?utm_source=chatgpt.com "Function calling - OpenAI API"
