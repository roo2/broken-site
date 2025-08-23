import httpx
from typing import Dict, Any

def http_check(url: str, method: str = "GET", follow_redirects: bool = True, timeout_sec: int = 10) -> Dict[str, Any]:
    out: Dict[str, Any] = {"url": url, "method": method}
    try:
        with httpx.Client(follow_redirects=follow_redirects, timeout=timeout_sec) as client:
            resp = client.request(method, url, headers={"User-Agent": "DiagBot/1.0"})
            out["status_code"] = resp.status_code
            out["final_url"] = str(resp.url)
            out["redirected"] = (str(resp.url) != url)
            # include a subset of headers for brevity
            out["headers"] = {k: v for k, v in resp.headers.items() if k.lower() in [
                "server","content-type","location","strict-transport-security",
                "x-frame-options","x-content-type-options","content-security-policy","referrer-policy"
            ]}
            out["body_sample"] = resp.text[:512]
    except Exception as e:
        out["error"] = str(e)
    return out
