# Sentix MDR: Autonomous Incident Detection & Role-Gated Governance

Enterprise security telemetry evaluation, blast-radius containment, and role-based execution.

---

## Executive Overview

### The Operational Challenge
Modern enterprise security teams face a fundamental operational trade-off:
- **Triage Fatigue:** Enterprises generate tens of thousands of authentication, API, and network telemetry events daily. Security operations analysts spend the majority of their shifts manually correlating IP addresses, directory records, and service meshes, leading to mean-time-to-respond (MTTR) figures exceeding 20 minutes per incident.
- **The Blast-Radius Risk:** Fully autonomous containment actions are dangerous in complex enterprise architectures. Null-routing an IP range or terminating an enterprise identity can inadvertently disrupt revenue-critical B2B partner EDI channels, production database replication, or executive single sign-on access.

### The Sentix Solution
Sentix MDR provides an automated decision engine that dynamically balances threat confidence against collateral operational disruption:
- **Objective Evaluation:** Ingests raw telemetry and computes calibrated threat probabilities alongside operational blast-radius metrics.
- **Three-Tier Governance Model:**
  - **Tier 1 (Automated Action):** High threat confidence with negligible blast radius. Containment is executed instantly at the perimeter edge without analyst intervention.
  - **Tier 2 (Drafted 1-Click Action):** Verified threats with moderate blast radius. Containment scripts and perimeter rules are drafted and routed exclusively to the designated authority (CISO, CTO, or Platform Lead) for single-click execution.
  - **Tier 3 (Technical Playbook):** High blast radius or systemic architecture drift where automated execution could cause operational outages. Generates prioritized, multi-step engineering remediation procedures and verification commands.
  - **Tier 0 (Benign Baseline):** Verified normal traffic filtered before alert ledgers to eliminate operational noise.

### Key Performance Indicators
- **Triage Latency:** Reduced from an industry average of 25 minutes to under 200 milliseconds.
- **Collateral Downtime:** Zero unauthorized disruptions on shared partner gateways or production clusters through deterministic blast-radius guardrails.
- **Role Isolation:** Strict per-persona scoping ensuring executives and infrastructure leads only see and authorize actions within their verified asset boundary.

---

## System Architecture

```
[ Ingested Security Telemetry ]
               │
               ▼
[ State Synthesizer & Topology Resolution ]
  Maps client IPs, user directories, subnets, and service criticality
               │
               ▼
[ Candidate Action Formulation & Dynamic Question Battery ]
  Formulates context-specific containment options and risk queries
               │
               ▼
[ Cognitive Jev Evaluation Engine ]
  Evaluates threat likelihood, blast radius, and action safety scores (<180ms)
               │
               ▼
[ Deterministic Decision Engine ]
  ├── Threat >= 0.75 and Blast < 0.20  ──► [ Tier 1: Machine Automated Execution ]
  ├── Threat >= 0.70 and Blast <= 0.70 ──► [ Tier 2: Role-Gated 1-Click Mitigation ]
  ├── Blast > 0.70 or Posture Drift    ──► [ Tier 3: Technical Mitigation Playbook ]
  └── Threat < 0.20                    ──► [ Tier 0: Benign Telemetry Filtered ]
               │
               ▼
[ Immutable SQLite Audit Ledger ] ◄──► [ Real-Time Next.js Governance Console ]
```

---

## Persona-Based Governance (RBAC Model)

Sentix enforces strict role separation so that decision interfaces display only the alerts and execution rights appropriate to each persona:

| Persona ID | Name | Role Title | Asset Authority Scope | Visible Tiers |
| :--- | :--- | :--- | :--- | :--- |
| `u_ciso` | Elena Rostova | Chief Information Security Officer | Enterprise SSO, Identity Governance, Executive Portals, B2B Partner Subnets | Tier 2, Tier 3 |
| `u_cto` | David Kim | Chief Technology Officer | Production Cloud Architecture, AWS Root Accounts, Production Aurora DB | Tier 2, Tier 3 |
| `u_devops` | Marcus Vance | Staff Platform / DevOps Tech Lead | Kubernetes Clusters, CI/CD Secrets, IAM Service Accounts | Tier 2, Tier 3 |
| `u_soc` | Sarah Jenkins | Incident Response / SOC Lead | Edge WAF, Cloudflare Policies, Ingress Telemetry, Threat Hunting | Tier 1, Tier 2, Tier 3 |
| `u_eng` | Alex Rivera | Senior Platform Engineer | Developer Workstations, Git Repositories, Staging API Keys | Tier 1, Tier 3 |

---

## Technical Specifications

### Backend Services
- **Framework:** FastAPI (Python 3.10+) with Uvicorn ASGI server.
- **Persistence:** SQLite database with indexed audit ledger, relational topology schema, and WAL mode.
- **Validation:** Pydantic v2 schemas for strict request/response data contracts.
- **Inference Engine:** TypeSafe Jev System-One Primitives (`Choice`, `Score`, `Noul`) with deterministic heuristic evaluation fallbacks.

### Frontend Console
- **Framework:** Next.js 16.3.6 (React 19, TypeScript).
- **Styling & Components:** Tailwind CSS with shadcn/ui components (Radix/Base UI primitives).
- **Layout Architecture:**
  - Single-line tabular density with zero text wrapping (`table-fixed`, proportional widths).
  - Synchronized single-surface vertical scrolling with sticky Incident Inspector.
  - Active persona context switcher dynamically filtering audit records and telemetry feeds.

---

## API Reference

### Telemetry Ingestion
- `POST /api/logs/ingest`
  Ingests a raw telemetry log, executes the cognitive evaluation pipeline, assigns a governance tier, records an audit entry if actionable, and returns the evaluation receipt.

### Telemetry Lake
- `GET /api/logs?limit=100&user_id={persona_id}`
  Retrieves chronological log events. Scoped to specific persona identities or fleet-wide for SOC analysts.

### Audit Ledger & Governance
- `GET /api/audit?limit=50&persona_id={persona_id}&tier={tier}`
  Queries decisions from the audit ledger. Evaluates persona authorization flags (`can_act`) and filters records to the actor's asset scope.
- `POST /api/audit/{id}/approve`
  Executes a drafted Tier 2 containment action. Verifies that the requesting actor matches the authorized persona ID before recording state transition to `EXECUTED_BY_OPERATOR`.

### Topology Introspection
- `GET /api/topology`
  Returns active enterprise topology facts: directory users, infrastructure nodes, client workstations, and network subnets.
- `POST /api/topology/reset`
  Resets logs and audit decision records back to a pristine baseline state for demonstration workflows.

---

## Quickstart & Local Deployment

### Prerequisites
- Python 3.10 or higher
- Node.js 18.0 or higher
- npm 9.0 or higher

### Automated Launch
Use the root execution script to start all services simultaneously:
```bash
./run.sh
```

This starts:
- **FastAPI Backend:** `http://localhost:8000` (OpenAPI specification at `/docs`)
- **Next.js Console:** `http://localhost:3000`

### Manual Execution

#### 1. Backend Service
```bash
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Console
```bash
cd frontend-next
npm run dev
```

#### 3. Telemetry Streamer (Optional)
To stream enterprise security logs with realistic pacing:
```bash
./venv/bin/python backend/scripts/stream_logs.py
```

---

## Verification & Testing

### Frontend Build & Lint Checks
```bash
cd frontend-next
npx tsc --noEmit
npm run lint
npm run build
```

### Backend Test Suite
```bash
./venv/bin/python -m pytest tests/
```

---

## License
Proprietary and confidential. Internal enterprise demonstration release.
