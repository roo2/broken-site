from typing import Dict, Any, List
import socket
import re

def hosting_provider_detect(domain: str, dns_records: Dict[str, Any] = None, tls_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Detect hosting provider based on DNS records, IP addresses, and TLS certificate information.
    Returns provider info with specific instructions and dashboard links, including certificate management.
    """
    
    providers = {
        "godaddy": {
            "name": "GoDaddy",
            "indicators": [
                r"godaddy\.com",
                r"secureserver\.net",
                r"gdns\.net",
                r"gdns\.com",
                r"godaddysites\.com"
            ],
            "dashboard_url": "https://sso.godaddy.com/",
            "instructions": "Log into your GoDaddy account and go to the DNS management section to update your records.",
            "support_url": "https://www.godaddy.com/help"
        },
        "cloudflare": {
            "name": "Cloudflare",
            "indicators": [
                r"cloudflare\.com",
                r"cloudflare\.net",
                r"1\.1\.1\.1",
                r"1\.0\.0\.1"
            ],
            "dashboard_url": "https://dash.cloudflare.com/",
            "instructions": "Access your Cloudflare dashboard and go to the DNS section to manage your records.",
            "support_url": "https://support.cloudflare.com/"
        },
        "aws": {
            "name": "Amazon Web Services (AWS)",
            "indicators": [
                r"amazonaws\.com",
                r"route53\.amazonaws\.com",
                r"elasticbeanstalk\.com",
                r"cloudfront\.net"
            ],
            "dashboard_url": "https://console.aws.amazon.com/",
            "instructions": "Log into AWS Console and navigate to Route 53 for DNS management.",
            "support_url": "https://aws.amazon.com/support/",
            "certificate_management": {
                "acm": {
                    "name": "AWS Certificate Manager (ACM)",
                    "detection": {
                        "issuer_patterns": [
                            r"Amazon",
                            r"Amazon Web Services",
                            r"ACM"
                        ],
                        "subject_patterns": [
                            r"Amazon",
                            r"ACM"
                        ]
                    },
                    "instructions": "1) Log into AWS Console at https://console.aws.amazon.com/, 2) Navigate to Certificate Manager (ACM), 3) Find your certificate and click 'Renew' or 'Request Certificate', 4) Follow the validation process",
                    "dashboard_url": "https://console.aws.amazon.com/acm/"
                },
                "certbot": {
                    "name": "Certbot (Let's Encrypt)",
                    "detection": {
                        "issuer_patterns": [
                            r"Let's Encrypt",
                            r"Let's Encrypt Authority",
                            r"ISRG"
                        ],
                        "subject_patterns": [
                            r"Let's Encrypt"
                        ]
                    },
                    "instructions": "Your certificate is managed by Certbot (Let's Encrypt). To renew: 1) SSH into your EC2 instance, 2) Run 'sudo certbot renew' to renew all certificates, 3) Or run 'sudo certbot renew --cert-name your-domain.com' for a specific certificate, 4) Restart your web server if needed (sudo systemctl reload nginx/apache2)",
                    "dashboard_url": None,
                    "support_url": "https://certbot.eff.org/instructions"
                }
            }
        },
        "google": {
            "name": "Google Cloud Platform",
            "indicators": [
                r"googleapis\.com",
                r"googleusercontent\.com",
                r"googlehosted\.com"
            ],
            "dashboard_url": "https://console.cloud.google.com/",
            "instructions": "Access Google Cloud Console and go to Cloud DNS to manage your records.",
            "support_url": "https://cloud.google.com/support"
        },
        "namecheap": {
            "name": "Namecheap",
            "indicators": [
                r"namecheap\.com",
                r"registrar-servers\.com"
            ],
            "dashboard_url": "https://ap.www.namecheap.com/",
            "instructions": "Log into your Namecheap account and go to Domain List > Manage > Advanced DNS.",
            "support_url": "https://www.namecheap.com/support/"
        },
        "hostgator": {
            "name": "HostGator",
            "indicators": [
                r"hostgator\.com",
                r"hostgator\.net"
            ],
            "dashboard_url": "https://portal.hostgator.com/",
            "instructions": "Access your HostGator control panel and navigate to DNS Zone Editor.",
            "support_url": "https://www.hostgator.com/support"
        },
        "bluehost": {
            "name": "Bluehost",
            "indicators": [
                r"bluehost\.com",
                r"bluehost\.net"
            ],
            "dashboard_url": "https://my.bluehost.com/",
            "instructions": "Log into your Bluehost control panel and go to the DNS Zone Editor.",
            "support_url": "https://www.bluehost.com/support"
        },
        "dreamhost": {
            "name": "DreamHost",
            "indicators": [
                r"dreamhost\.com",
                r"dreamhosters\.com"
            ],
            "dashboard_url": "https://panel.dreamhost.com/",
            "instructions": "Access your DreamHost panel and navigate to Domains > DNS.",
            "support_url": "https://help.dreamhost.com/"
        },
        "digitalocean": {
            "name": "DigitalOcean",
            "indicators": [
                r"digitalocean\.com",
                r"ondigitalocean\.app"
            ],
            "dashboard_url": "https://cloud.digitalocean.com/",
            "instructions": "Log into DigitalOcean and go to Networking > Domains to manage DNS.",
            "support_url": "https://www.digitalocean.com/support"
        },
        "vercel": {
            "name": "Vercel",
            "indicators": [
                r"vercel\.app",
                r"vercel\.com"
            ],
            "dashboard_url": "https://vercel.com/dashboard",
            "instructions": "Access your Vercel dashboard and go to your project's Domains section.",
            "support_url": "https://vercel.com/support"
        },
        "netlify": {
            "name": "Netlify",
            "indicators": [
                r"netlify\.app",
                r"netlify\.com"
            ],
            "dashboard_url": "https://app.netlify.com/",
            "instructions": "Log into Netlify and go to your site's Domain management section.",
            "support_url": "https://docs.netlify.com/"
        }
    }
    
    detected_providers = []
    
    # Check DNS records if provided
    if dns_records:
        for record_type, records in dns_records.get("records", {}).items():
            if isinstance(records, list):
                for record in records:
                    if isinstance(record, str):
                        for provider_id, provider_info in providers.items():
                            for indicator in provider_info["indicators"]:
                                if re.search(indicator, record, re.IGNORECASE):
                                    if provider_id not in [p["id"] for p in detected_providers]:
                                        detected_providers.append({
                                            "id": provider_id,
                                            "name": provider_info["name"],
                                            "confidence": "high",
                                            "detected_from": f"DNS {record_type} record",
                                            "dashboard_url": provider_info["dashboard_url"],
                                            "instructions": provider_info["instructions"],
                                            "support_url": provider_info["support_url"]
                                        })
    
    # Check nameservers specifically
    if dns_records and "NS" in dns_records.get("records", {}):
        ns_records = dns_records["records"]["NS"]
        if isinstance(ns_records, list):
            for ns_record in ns_records:
                if isinstance(ns_record, str):
                    for provider_id, provider_info in providers.items():
                        for indicator in provider_info["indicators"]:
                            if re.search(indicator, ns_record, re.IGNORECASE):
                                if provider_id not in [p["id"] for p in detected_providers]:
                                    detected_providers.append({
                                        "id": provider_id,
                                        "name": provider_info["name"],
                                        "confidence": "high",
                                        "detected_from": "nameserver",
                                        "dashboard_url": provider_info["dashboard_url"],
                                        "instructions": provider_info["instructions"],
                                        "support_url": provider_info["support_url"]
                                    })
    
    # Try to resolve domain and check IP-based detection
    try:
        ip_addresses = socket.gethostbyname_ex(domain)[2]
        for ip in ip_addresses:
            for provider_id, provider_info in providers.items():
                for indicator in provider_info["indicators"]:
                    if re.search(indicator, ip, re.IGNORECASE):
                        if provider_id not in [p["id"] for p in detected_providers]:
                            detected_providers.append({
                                "id": provider_id,
                                "name": provider_info["name"],
                                "confidence": "medium",
                                "detected_from": f"IP address {ip}",
                                "dashboard_url": provider_info["dashboard_url"],
                                "instructions": provider_info["instructions"],
                                "support_url": provider_info["support_url"]
                            })
    except Exception:
        pass
    
    # Detect certificate management method if TLS info is provided
    certificate_management = None
    if tls_info and detected_providers:
        primary_provider = detected_providers[0]
        provider_id = primary_provider["id"]
        
        if provider_id in providers and "certificate_management" in providers[provider_id]:
            cert_management_options = providers[provider_id]["certificate_management"]
            
            # Check certificate issuer and subject
            issuer = tls_info.get("issuer", "")
            subject = tls_info.get("subject", "")
            
            for cert_type, cert_info in cert_management_options.items():
                detection = cert_info["detection"]
                
                # Check issuer patterns
                issuer_match = any(re.search(pattern, issuer, re.IGNORECASE) 
                                  for pattern in detection["issuer_patterns"])
                
                # Check subject patterns
                subject_match = any(re.search(pattern, subject, re.IGNORECASE) 
                                   for pattern in detection["subject_patterns"])
                
                if issuer_match or subject_match:
                    certificate_management = {
                        "type": cert_type,
                        "name": cert_info["name"],
                        "instructions": cert_info["instructions"],
                        "dashboard_url": cert_info.get("dashboard_url"),
                        "support_url": cert_info.get("support_url")
                    }
                    break
    
    # If no specific provider detected, check for common patterns
    if not detected_providers:
        # Check for common hosting patterns
        common_patterns = {
            "shared_hosting": {
                "name": "Shared Hosting Provider",
                "indicators": [r"cpanel", r"plesk", r"webmail"],
                "instructions": "Contact your hosting provider's support for DNS management assistance.",
                "support_url": "https://www.google.com/search?q=hosting+provider+support"
            }
        }
        
        # This would require additional HTTP checks to detect cPanel/Plesk
        # For now, we'll return a generic response
    
    return {
        "domain": domain,
        "detected_providers": detected_providers,
        "primary_provider": detected_providers[0] if detected_providers else None,
        "certificate_management": certificate_management,
        "total_providers": len(detected_providers)
    }
