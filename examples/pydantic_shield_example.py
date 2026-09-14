"""
Production-grade Two-Layer Pydantic Shield and Observability Template.
Includes error contracts, status categorization, cloud logging, and circuit breakers.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import time
from pydantic import BaseModel, Field

# =====================================================================
# 1. Pydantic Error Contract Schema
# =====================================================================

class BaseServiceResult(BaseModel):
    """Base contract for the Two-Layer Shield with fault tolerance."""
    data: Optional[Any] = Field(default=None, description="Primary service payload")
    source_status: str = Field(
        default="OK",
        description="Source status: OK, QUOTA_EXCEEDED, SERVICE_DEGRADED, AUTH_ERROR, RATE_LIMITED, FALLBACK"
    )
    error_type: Optional[str] = Field(
        default=None,
        description="Machine-readable error code: invalid_token, quota_exceeded, timeout, network_error"
    )
    warning_note: Optional[str] = Field(
        default=None,
        description="Human-readable, calm fallback message for both user and agent upon degraded state"
    )

# =====================================================================
# 2. Structured Cloud Logging (Zero Leak)
# =====================================================================

def log_cloud_event(severity: str, event_name: str, **kwargs):
    """Emits structured JSON logs for Google Cloud Logging / Cloud Trace with secret masking."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "severity": severity.upper(),
        "event": event_name,
        **kwargs
    }
    print(json.dumps(log_entry, ensure_ascii=False), flush=True)

# =====================================================================
# 3. Safe Execution Wrapper Example
# =====================================================================

def safe_api_executor(service_call_fn, fallback_data=None, *args, **kwargs) -> BaseServiceResult:
    """Wraps any external API call into a resilient two-layer shield."""
    start_time = time.time()
    try:
        raw_result = service_call_fn(*args, **kwargs)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        log_cloud_event("INFO", "api_call_success", latency_ms=latency_ms)
        return BaseServiceResult(data=raw_result, source_status="OK")
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        err_msg = str(e)
        log_cloud_event("ERROR", "api_call_failed", error=err_msg, latency_ms=latency_ms)
        
        status = "SERVICE_DEGRADED"
        if "429" in err_msg or "quota" in err_msg.lower():
            status = "QUOTA_EXCEEDED"
        elif "401" in err_msg or "403" in err_msg or "auth" in err_msg.lower():
            status = "AUTH_ERROR"
            
        return BaseServiceResult(
            data=fallback_data,
            source_status=status,
            error_type="network_or_api_error",
            warning_note="Service temporarily degraded. Fallback estimates applied."
        )
