import socket, ssl, datetime
from typing import Dict, Any

def tls_probe(host: str, port: int = 443, sni: bool = True) -> Dict[str, Any]:
    ctx = ssl.create_default_context()
    result: Dict[str, Any] = {"host": host, "port": port}

    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=(host if sni else None)) as ssock:
                cert = ssock.getpeercert()
                result["tls_version"] = ssock.version()
                if cert:
                    result["subject"] = dict(x[0] for x in cert.get("subject", []))
                    result["issuer"] = dict(x[0] for x in cert.get("issuer", []))
                    not_after = cert.get("notAfter")
                    result["not_after"] = not_after
                    if not_after:
                        # Convert to ISO date
                        dt = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        result["days_until_expiry"] = (dt - datetime.datetime.utcnow()).days
                else:
                    result["warning"] = "No certificate returned"
    except Exception as e:
        result["error"] = str(e)
    return result
