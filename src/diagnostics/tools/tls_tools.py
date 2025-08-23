import socket, ssl, datetime
from typing import Dict, Any

def tls_probe(host: str, port: int = 443, sni: bool = True) -> Dict[str, Any]:
    ctx = ssl.create_default_context()
    # Disable certificate verification to allow extraction of expired certificates
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    result: Dict[str, Any] = {"host": host, "port": port}

    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=(host if sni else None)) as ssock:
                result["tls_version"] = ssock.version()
                
                # Try to get certificate info - first try with verification enabled for better parsing
                try:
                    # Create a new context with verification for parsing
                    parse_ctx = ssl.create_default_context()
                    parse_ctx.check_hostname = False
                    parse_ctx.verify_mode = ssl.CERT_REQUIRED
                    
                    with socket.create_connection((host, port), timeout=10) as parse_sock:
                        with parse_ctx.wrap_socket(parse_sock, server_hostname=(host if sni else None)) as parse_ssock:
                            cert = parse_ssock.getpeercert()
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
                except ssl.SSLCertVerificationError:
                    # Certificate verification failed (likely expired), try binary format
                    cert_bin = ssock.getpeercert(binary_form=True)
                    if cert_bin:
                        cert = ssl.DER_cert_to_PEM_cert(cert_bin)
                        # Parse the PEM certificate
                        from cryptography import x509
                        from cryptography.hazmat.backends import default_backend
                        
                        try:
                            cert_obj = x509.load_pem_x509_certificate(cert.encode(), default_backend())
                            
                            # Extract subject
                            subject_dict = {}
                            for name in cert_obj.subject:
                                subject_dict[name.oid._name] = name.value
                            result["subject"] = subject_dict
                            
                            # Extract issuer
                            issuer_dict = {}
                            for name in cert_obj.issuer:
                                issuer_dict[name.oid._name] = name.value
                            result["issuer"] = issuer_dict
                            
                            # Extract expiry date
                            not_after = cert_obj.not_valid_after
                            result["not_after"] = not_after.isoformat()
                            result["days_until_expiry"] = (not_after - datetime.datetime.now(not_after.tzinfo)).days
                            
                        except ImportError:
                            # Fallback if cryptography library is not available
                            result["warning"] = "Certificate found but cryptography library not available for parsing"
                        except Exception as e:
                            result["warning"] = f"Error parsing certificate: {str(e)}"
                    else:
                        result["warning"] = "No certificate returned"
                except Exception as e:
                    result["warning"] = f"Error getting certificate: {str(e)}"
    except Exception as e:
        result["error"] = str(e)
    return result
