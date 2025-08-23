from typing import List, Dict, Any
import dns.resolver

def _safe_query(domain: str, rtype: str):
    try:
        answers = dns.resolver.resolve(domain, rtype, raise_on_no_answer=False)
        return [a.to_text() for a in answers] if answers else []
    except Exception as e:
        return {"error": str(e)}

def dns_lookup(domain: str, record_types: List[str]) -> Dict[str, Any]:
    data: Dict[str, Any] = {"domain": domain, "records": {}}
    for r in record_types:
        data["records"][r] = _safe_query(domain, r)
    return data


