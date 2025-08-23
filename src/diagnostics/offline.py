import logging
from typing import Dict, Any, List
from .tools import dns_lookup, tls_probe, http_check
from .schemas import DiagnosticReport, Issue

logger = logging.getLogger(__name__)

def run_offline_diagnosis(target: str) -> DiagnosticReport:
    logger.info(f"Starting offline diagnosis for target: {target}")
    
    # heuristic: if target includes scheme, treat as URL; else domain
    is_url = target.startswith("http://") or target.startswith("https://")
    domain = target.split("://", 1)[1].split("/")[0] if is_url else target
    
    logger.info(f"Parsed target - is_url: {is_url}, domain: {domain}")

    issues: List[Issue] = []

    logger.info("Running DNS lookup...")
    dns = dns_lookup(domain, ["A","AAAA","CNAME","MX","NS","TXT"])
    logger.info("DNS lookup completed")
    
    logger.info("Running HTTP check...")
    http = http_check(target if is_url else f"https://{domain}")
    logger.info("HTTP check completed")
    
    logger.info("Running TLS probe...")
    tls = tls_probe(domain, 443, sni=True)
    logger.info("TLS probe completed")

    # Basic findings
    if isinstance(dns["records"].get("A"), dict) and "error" in dns["records"]["A"]:
        issues.append(Issue(
            id="dns_a_lookup_error",
            category="DNS", severity="high",
            evidence=f"A lookup error: {dns['records']['A']['error']}",
            recommended_fix="Verify domain exists and is publicly resolvable; check registrar/NS."
        ))

    if "error" in http:
        issues.append(Issue(
            id="http_error",
            category="HTTP", severity="high",
            evidence=f"HTTP error: {http['error']}",
            recommended_fix="Confirm the host is reachable (firewall, DNS, service up)."
        ))
    else:
        if http.get("status_code", 200) >= 500:
            issues.append(Issue(
                id="server_error",
                category="HTTP", severity="high",
                evidence=f"Status code {http['status_code']} at {http['final_url']}",
                recommended_fix="Inspect server logs for stack traces; roll back recent changes."
            ))

    if "error" in tls:
        issues.append(Issue(
            id="tls_handshake_error",
            category="TLS", severity="high",
            evidence=f"TLS error: {tls['error']}",
            recommended_fix="Check certificate chain, SNI config, and TLS versions."
        ))
    else:
        days = tls.get("days_until_expiry")
        if isinstance(days, int) and days <= 14:
            issues.append(Issue(
                id="cert_expiring_soon",
                category="TLS", severity="medium",
                evidence=f"Certificate expires in {days} day(s)",
                recommended_fix="Renew your certificate (ACME/Let’s Encrypt) and reload web server."
            ))



    logger.info(f"Found {len(issues)} issues during offline diagnosis")
    
    summary = "Automated diagnostics completed. "               f"Found {len(issues)} issue(s)."
    
    logger.info("Offline diagnosis completed successfully")
    return DiagnosticReport(
        summary=summary,
        issues=issues,
        artifacts={
            "screenshots": [],
            "raw_samples": {
                "dns": dns,
                "http": http,
                "tls": tls,
            }
        }
    )
