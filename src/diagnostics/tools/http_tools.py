import httpx
import re
from typing import Dict, Any

def detect_web_server(headers: Dict[str, str]) -> Dict[str, Any]:
    """Detect web server from headers and other indicators"""
    server_info = {"type": "unknown", "version": "unknown", "details": ""}
    
    # Check Server header
    server_header = headers.get("server", "").lower()
    if "apache" in server_header:
        server_info["type"] = "Apache"
        # Extract version if present
        version_match = re.search(r'apache[/\s](\d+\.\d+)', server_header, re.IGNORECASE)
        if version_match:
            server_info["version"] = version_match.group(1)
    elif "nginx" in server_header:
        server_info["type"] = "Nginx"
        version_match = re.search(r'nginx[/\s](\d+\.\d+)', server_header, re.IGNORECASE)
        if version_match:
            server_info["version"] = version_match.group(1)
    elif "iis" in server_header or "microsoft" in server_header:
        server_info["type"] = "IIS"
        version_match = re.search(r'iis[/\s](\d+)', server_header, re.IGNORECASE)
        if version_match:
            server_info["version"] = version_match.group(1)
    elif "cloudflare" in server_header:
        server_info["type"] = "Cloudflare"
    elif "cloudfront" in server_header:
        server_info["type"] = "CloudFront"
    
    return server_info

def detect_programming_language(headers: Dict[str, str], body: str) -> Dict[str, Any]:
    """Detect programming language and framework from headers and body"""
    lang_info = {"language": "unknown", "framework": "unknown", "details": ""}
    
    # Check headers for language indicators
    content_type = headers.get("content-type", "").lower()
    x_powered_by = headers.get("x-powered-by", "").lower()
    
    # PHP detection
    if "php" in x_powered_by or "php" in content_type:
        lang_info["language"] = "PHP"
        # Detect common PHP frameworks
        if "wordpress" in body.lower():
            lang_info["framework"] = "WordPress"
        elif "laravel" in body.lower() or "laravel" in x_powered_by:
            lang_info["framework"] = "Laravel"
        elif "drupal" in body.lower():
            lang_info["framework"] = "Drupal"
        elif "joomla" in body.lower():
            lang_info["framework"] = "Joomla"
        elif "magento" in body.lower():
            lang_info["framework"] = "Magento"
    
    # Python detection
    elif "python" in x_powered_by or "django" in x_powered_by or "flask" in x_powered_by:
        lang_info["language"] = "Python"
        if "django" in x_powered_by or "django" in body.lower():
            lang_info["framework"] = "Django"
        elif "flask" in x_powered_by or "flask" in body.lower():
            lang_info["framework"] = "Flask"
        elif "fastapi" in body.lower():
            lang_info["framework"] = "FastAPI"
    
    # Node.js detection
    elif "node" in x_powered_by or "express" in x_powered_by:
        lang_info["language"] = "JavaScript (Node.js)"
        if "express" in x_powered_by or "express" in body.lower():
            lang_info["framework"] = "Express.js"
        elif "next.js" in body.lower() or "nextjs" in body.lower():
            lang_info["framework"] = "Next.js"
        elif "react" in body.lower():
            lang_info["framework"] = "React"
    
    # Ruby detection
    elif "ruby" in x_powered_by or "rails" in x_powered_by:
        lang_info["language"] = "Ruby"
        if "rails" in x_powered_by or "rails" in body.lower():
            lang_info["framework"] = "Ruby on Rails"
    
    # Java detection
    elif "java" in x_powered_by or "tomcat" in x_powered_by or "jboss" in x_powered_by:
        lang_info["language"] = "Java"
        if "spring" in x_powered_by or "spring" in body.lower():
            lang_info["framework"] = "Spring"
        elif "tomcat" in x_powered_by:
            lang_info["framework"] = "Apache Tomcat"
    
    # .NET detection
    elif "asp.net" in x_powered_by or "dotnet" in x_powered_by:
        lang_info["language"] = "C# (.NET)"
        if "asp.net" in x_powered_by:
            lang_info["framework"] = "ASP.NET"
    
    # Static site detection
    elif "static" in content_type or len(body) < 1000:
        # Check for common static site generators
        if "jekyll" in body.lower():
            lang_info["language"] = "Static (Jekyll)"
            lang_info["framework"] = "Jekyll"
        elif "hugo" in body.lower():
            lang_info["language"] = "Static (Hugo)"
            lang_info["framework"] = "Hugo"
        elif "gatsby" in body.lower():
            lang_info["language"] = "Static (Gatsby)"
            lang_info["framework"] = "Gatsby"
        else:
            lang_info["language"] = "Static HTML"
    
    return lang_info

def detect_domain_expired_page(body: str, url: str) -> Dict[str, Any]:
    """Detect domain expired/parking pages from HTML body and URL"""
    expired_info = {"is_expired_page": False, "provider": "unknown", "details": ""}
    
    body_lower = body.lower()
    
    # GoDaddy expired domain detection
    if ("lander" in url.lower() or "/lander" in url.lower()) and (
        "landing page" in body_lower or 
        "domain expired" in body_lower or
        "parking-lander" in body_lower or
        "wsimg.com/parking-lander" in body_lower or
        "window.lander_system" in body_lower or
        "window.lander_system = \"pw\"" in body_lower
    ):
        expired_info["is_expired_page"] = True
        expired_info["provider"] = "GoDaddy"
        expired_info["details"] = "Domain has expired and is showing GoDaddy parking page"
    
    # GoDaddy redirect page detection (initial expired domain page)
    elif "window.location.href=\"/lander\"" in body or "window.onload=function(){window.location.href=\"/lander\"}" in body:
        expired_info["is_expired_page"] = True
        expired_info["provider"] = "GoDaddy"
        expired_info["details"] = "Domain has expired and is redirecting to GoDaddy parking page"
    
    # Namecheap expired domain detection
    elif ("parking" in url.lower() or "expired" in url.lower()) and (
        "namecheap" in body_lower or
        "domain parking" in body_lower or
        "expired domain" in body_lower
    ):
        expired_info["is_expired_page"] = True
        expired_info["provider"] = "Namecheap"
        expired_info["details"] = "Domain has expired and is showing Namecheap parking page"
    
    # Google Domains expired detection
    elif ("google" in body_lower and "domains" in body_lower) and (
        "domain expired" in body_lower or
        "parking" in body_lower or
        "googleadservices" in body_lower
    ):
        expired_info["is_expired_page"] = True
        expired_info["provider"] = "Google Domains"
        expired_info["details"] = "Domain has expired and is showing Google Domains parking page"
    
    # Cloudflare expired domain detection
    elif ("cloudflare" in body_lower) and (
        "domain expired" in body_lower or
        "parking" in body_lower or
        "1101" in body_lower  # Cloudflare error code for expired domains
    ):
        expired_info["is_expired_page"] = True
        expired_info["provider"] = "Cloudflare"
        expired_info["details"] = "Domain has expired and is showing Cloudflare parking page"
    
    # Generic expired domain patterns
    elif any(pattern in body_lower for pattern in [
        "domain expired",
        "domain has expired", 
        "domain is expired",
        "expired domain",
        "domain parking",
        "parking page",
        "domain for sale",
        "buy this domain",
        "domain auction"
    ]):
        expired_info["is_expired_page"] = True
        expired_info["provider"] = "Generic"
        expired_info["details"] = "Domain appears to be expired or parked"
    
    # Check for common parking page indicators
    elif any(indicator in body_lower for indicator in [
        "parking-lander",
        "domain parking",
        "domain auction",
        "domain marketplace",
        "domain broker",
        "domain registrar"
    ]):
        expired_info["is_expired_page"] = True
        expired_info["provider"] = "Unknown"
        expired_info["details"] = "Domain appears to be parked or expired"
    
    return expired_info

def detect_cms_and_plugins(body: str) -> Dict[str, Any]:
    """Detect CMS and plugins from HTML body"""
    cms_info = {"cms": "unknown", "plugins": [], "themes": [], "details": ""}
    
    body_lower = body.lower()
    
    # WordPress detection
    if "wp-content" in body_lower or "wp-includes" in body_lower or "wordpress" in body_lower:
        cms_info["cms"] = "WordPress"
        
        # Detect WordPress version
        wp_version_match = re.search(r'<meta name="generator" content="WordPress ([^"]+)"', body, re.IGNORECASE)
        if wp_version_match:
            cms_info["version"] = wp_version_match.group(1)
        
        # Detect common plugins
        plugins = []
        if "woocommerce" in body_lower:
            plugins.append("WooCommerce")
        if "yoast" in body_lower or "yoast seo" in body_lower:
            plugins.append("Yoast SEO")
        if "contact-form-7" in body_lower or "wpcf7" in body_lower:
            plugins.append("Contact Form 7")
        if "jetpack" in body_lower:
            plugins.append("Jetpack")
        if "elementor" in body_lower:
            plugins.append("Elementor")
        cms_info["plugins"] = plugins
        
        # Detect theme
        theme_match = re.search(r'wp-content/themes/([^/"]+)', body, re.IGNORECASE)
        if theme_match:
            cms_info["themes"] = [theme_match.group(1)]
    
    # Drupal detection
    elif "drupal" in body_lower:
        cms_info["cms"] = "Drupal"
        drupal_version_match = re.search(r'Drupal ([0-9.]+)', body, re.IGNORECASE)
        if drupal_version_match:
            cms_info["version"] = drupal_version_match.group(1)
    
    # Joomla detection
    elif "joomla" in body_lower:
        cms_info["cms"] = "Joomla"
        joomla_version_match = re.search(r'Joomla! ([0-9.]+)', body, re.IGNORECASE)
        if joomla_version_match:
            cms_info["version"] = joomla_version_match.group(1)
    
    # Magento detection
    elif "magento" in body_lower:
        cms_info["cms"] = "Magento"
        magento_version_match = re.search(r'Magento/([0-9.]+)', body, re.IGNORECASE)
        if magento_version_match:
            cms_info["version"] = magento_version_match.group(1)
    
    return cms_info

def http_check(url: str, method: str = "GET", follow_redirects: bool = True, timeout_sec: int = 10) -> Dict[str, Any]:
    out: Dict[str, Any] = {"url": url, "method": method}
    try:
        with httpx.Client(follow_redirects=follow_redirects, timeout=timeout_sec) as client:
            resp = client.request(method, url, headers={"User-Agent": "DiagBot/1.0"})
            out["status_code"] = resp.status_code
            out["final_url"] = str(resp.url)
            out["redirected"] = (str(resp.url) != url)
            
            # Get all headers for analysis
            all_headers = {k: v for k, v in resp.headers.items()}
            out["headers"] = {k: v for k, v in all_headers.items() if k.lower() in [
                "server","content-type","location","strict-transport-security",
                "x-frame-options","x-content-type-options","content-security-policy","referrer-policy",
                "x-powered-by"
            ]}
            
            body_text = resp.text
            out["body_sample"] = body_text[:512]
            
            # Detect web server
            out["web_server"] = detect_web_server(all_headers)
            
            # Detect programming language and framework
            out["technology"] = detect_programming_language(all_headers, body_text)
            
            # Detect CMS and plugins
            out["cms_info"] = detect_cms_and_plugins(body_text)
            
            # Detect domain expired/parking pages
            out["domain_status"] = detect_domain_expired_page(body_text, str(resp.url))
            
    except Exception as e:
        out["error"] = str(e)
    return out
