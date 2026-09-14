# 🛡️ Agentic API Discovery & Two-Layer Shield Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-e92063.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Author](https://img.shields.io/badge/Architect-Mikhail%20Azhyshchev-black.svg)](https://azhyshchev.de)

> **The Engineering Standard for Integrating Third-Party, Legacy, and Partner APIs into Multi-Agent Systems without Hallucinations, 5xx Crashes, or Secret Leaks.**

---

## 🛑 The Problem: Why Direct LLM-to-API Integrations Fail

In enterprise operations and post-acquisition environments, AI agents frequently interact with fragmented legacy APIs (CRMs, ERPs, billing gateways, booking engines). 

Naive implementations expose raw API calls directly to language models, leading to severe production failures:
1. **Unhandled 4xx/5xx & Rate Limits:** When a legacy endpoint returns an undocumented 429 Too Many Requests or 502 Bad Gateway, the agent run crashes.
2. **Schema Drift & Hallucinations:** Missing fields, camelCase/snake_case mismatches, or unexpected null values cause silent runtime deserialization errors.
3. **Mutating State Accidents:** Agents triggering unvalidated POST, PATCH, or DELETE requests with malformed payloads.
4. **Credential & PII Leaks:** Raw API tokens, session headers, and customer IBANs/names leaking into LLM prompt histories and log traces.

---

## 🏛️ The Solution: The Two-Layer Shield Architecture

This framework establishes an engineering protocol where **no agent directly interacts with an unshielded external endpoint**.

`mermaid
flowchart TD
    subgraph Discovery [Phase 1: API Discovery & Probe]
        D0[Official Docs / OpenAPI Specs] --> D1[probe_endpoints.py]
        D1 -->|Automated Live Probing| D2[Raw Audit Dump: 200 OK + 4xx/5xx]
    end

    subgraph Layer1 [Phase 2: Layer 1 - Deterministic Code Shield]
        D2 --> L1[datamodel-codegen]
        L1 --> L2[Pydantic v2 Strict Error Contracts]
        L2 --> L3[Timeouts & Circuit Breaker Wrapper]
        L3 --> L4[Masked Cloud Logging - Zero Leak]
    end

    subgraph Layer2 [Phase 3: Layer 2 - Cognitive Instruction Shield]
        L4 --> A1[Agent Tool Execution]
        A1 -->|source_status: OK / RATE_LIMITED / TIMEOUT| A2[Cognitive Graceful Degradation]
        A2 --> A3[Clear User Output with Transaction ID]
    end
`

---

## 📦 Core Pipeline: 3 Phases to Production

### Phase 1: API Discovery & Full Endpoint Probing
* **Step 0 — Primary Source Audit:** Extract official developer docs, OpenAPI/Swagger specifications, or official GitHub SDKs.
* **Step 1 — Probing Runner (scripts/probe_endpoints.py):** Automatically probe live endpoints with real test payloads. Capture and store actual JSON response schemas for both successful operations (200 OK) and error states (400, 401, 403, 404, 429, 500).
* **Step 2 — Ingress Security Gate:** Enforce authentication guards (Header(x_internal_secret) or OAuth2 Bearer tokens) before exposing endpoints outside local development.

### Phase 2: Layer 1 — Deterministic Code & Observability Shield
* **Automated Contract Generation:** Generate strict Pydantic v2 models via datamodel-codegen preserving 100% of payload attributes (preventing loss of vendor error codes or warnings).
* **Safe Service Wrapper (ServiceResult[T]):** Wrap all network interactions in strict error contracts with normalized statuses:
  - OK
  - RATE_LIMITED
  - AUTH_ERROR
  - TIMEOUT
  - FALLBACK
* **Zero-Leak Sanitization:** Automatic redaction of sensitive credentials, API keys, and customer PII before sending structured logs to Google Cloud Logging.

### Phase 3: Layer 2 — Cognitive Instruction Shield
Teach the agent how to handle bounded return states gracefully:
* If source_status == 'RATE_LIMITED': The agent switches to cached or estimated calculations without panicking.
* If source_status == 'AUTH_ERROR': The agent asks the operator for credential renewal instead of re-trying blindly in an infinite loop.
* If a mutation is requested: The action is staged in a PAUSED state by default with hardcoded budget caps.

---

## 🚀 Quickstart

### 1. Installation
`ash
git clone https://github.com/Azhy34/api-discovery-framework.git
cd api-discovery-framework
pip install -r requirements.txt
`

### 2. Probe Endpoints & Capture Error Schemas
Edit scripts/probe_endpoints.py with your candidate endpoints and run:
`ash
python scripts/probe_endpoints.py
`
This generates 
aw_endpoints_audit.json containing latency benchmarks and real payload schemas.

### 3. Generate Pydantic Models (Zero-Install Sandbox)
`ash
uvx --from datamodel-code-generator datamodel-codegen \
  --input raw_endpoints_audit.json \
  --input-file-type json \
  --output models.py \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated \
  --snake-case-field \
  --use-default
`

### 4. Implement the Two-Layer Shield
See 
eferences/pydantic_shield_template.py for a drop-in implementation of safe_api_executor and ServiceResult[T].

---

## 📂 Repository Layout

`	ext
api-discovery-framework/
├── SKILL.md                                 # Complete Agent Skill Definition for Claude Code / Antigravity / Gemini CLI
├── requirements.txt                         # Runtime dependencies
├── scripts/
│   └── probe_endpoints.py                   # Automated latency & payload audit probe
└── references/
    ├── pydantic_shield_template.py          # Production Two-Layer Pydantic Shield & Cloud Logger
    └── google_travel_multi_aggregator.md    # Real-world case study: Multi-Aggregator with Zero API Costs
`

---

## 👨‍💻 Author

**Mikhail Azhyshchev**  
*AI Solutions Engineer | Multi-Agent Systems & Cloud Automation*  
- 🌐 Website: [azhyshchev.de](https://azhyshchev.de)  
- 📜 Google Cloud Certifications: [azhyshchev.de/certifications/](https://azhyshchev.de/certifications/)  
- 💼 LinkedIn: [linkedin.com/in/azhyshchev](https://linkedin.com/in/azhyshchev)  

---

## 📄 License
MIT License. Free for commercial and open-source use.
