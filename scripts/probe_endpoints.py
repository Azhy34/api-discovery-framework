"""
Universal automated probing script for raw API endpoints.
Measures latency, captures live 200 OK payloads and 4xx/5xx error structures to generate Pydantic shields.
"""

import json
import time
import requests
from typing import Dict, Any, List, Optional

def probe_endpoint(
    name: str, 
    method: str, 
    url: str, 
    headers: Optional[Dict[str, str]] = None, 
    params: Optional[Dict[str, Any]] = None, 
    json_body: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Probes an endpoint and returns detailed response structure with real payload keys."""
    start = time.time()
    try:
        resp = requests.request(
            method=method, 
            url=url, 
            headers=headers, 
            params=params, 
            json=json_body, 
            timeout=15
        )
        latency_ms = round((time.time() - start) * 1000, 2)
        
        try:
            payload = resp.json()
        except Exception:
            payload = {"raw_text": resp.text[:1000]}
            
        return {
            "name": name,
            "url": url,
            "method": method,
            "status_code": resp.status_code,
            "latency_ms": latency_ms,
            "success": resp.status_code == 200,
            "keys_returned": list(payload.keys()) if isinstance(payload, dict) else f"list_len_{len(payload)}",
            "raw_payload": payload
        }
    except Exception as e:
        return {
            "name": name,
            "url": url,
            "method": method,
            "status_code": 0,
            "latency_ms": round((time.time() - start) * 1000, 2),
            "success": False,
            "error": str(e)
        }

def run_endpoints_probe(endpoints: List[Dict[str, Any]], output_file: str = "raw_endpoints_audit.json"):
    """Runs batch probing across a list of endpoints and writes JSON audit report."""
    results = []
    print(f"🚀 Starting audit across {len(endpoints)} endpoints...")
    for ep in endpoints:
        print(f"  • Probing: [{ep.get('method', 'GET')}] {ep.get('name')} ...")
        res = probe_endpoint(
            name=ep["name"],
            method=ep.get("method", "GET"),
            url=ep["url"],
            headers=ep.get("headers"),
            params=ep.get("params"),
            json_body=ep.get("json_body")
        )
        results.append(res)
        status_icon = "✅" if res["success"] else "⚠️"
        print(f"    {status_icon} HTTP {res['status_code']} | Latency: {res['latency_ms']} ms")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Full audit dump successfully saved to: {output_file}")
    return results

if __name__ == "__main__":
    print("probe_endpoints runner initialized.")
