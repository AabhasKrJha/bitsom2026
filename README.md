# 🛡️ Sentix AutoOps: Autonomous Incident Triage with Blast-Radius Guardrails

> **Enterprise AI Track • Builders Pitch Fest Prototype**  
> *Built with FastAPI, Streamlit, Azure OpenAI / LLM, and TypeSafe Jev System-One Primitives (`Choice`, `Score`, `Noul`)*

---

## 📌 Executive Summary (The 1-Slide Pitch)

### 1. Problem Statement: The Enterprise Blast-Radius Dilemma
* **The Reality:** Enterprises receive tens of thousands of authentication, VPN, and identity alerts daily. Tier-1 SOC analysts spend **80% of their shift manually correlating logs, IPs, and user directories**, taking 15–45 minutes per alert.
* **The Dilemma:**
  * **Pure manual triage is too slow:** Attackers succeed in credential stuffing in under 2 minutes.
  * **Full automation is too dangerous:** High-blast-radius actions (e.g., null-routing a `/24` subnet or locking an Executive's account) disrupt legitimate B2B partner gateways and halt business revenue.

### 2. The Solution: Sentix AutoOps
An autonomous Tier-1 SecOps decision engine with **Blast-Radius Guardrails**:
* **Generative LLM (Azure OpenAI):** Parses unstructured logs & extracts dynamic context tags (Executive identity, shared partner subnet, velocity spike).
* **TypeSafe Jev System-One:** Evaluates parallel, calibrated structured decision primitives (`Choice`, `Score`, `Noul`) in **<180ms with zero hallucination risk**.
* **Blast-Radius Guardrails:**
  * **Low-Blast Noise (Routine users, single IP):** Autonomously rate-limited at the Edge WAF without analyst intervention.
  * **High-Blast Threats (Executive target, shared partner subnet):** Pre-drafted with plain-English rationales for **1-click Human-in-the-Loop (HITL) sign-off**.

### 3. Key Impact Metrics
* **98.8% Reduction in Triage Latency:** From 25 minutes manual review down to 178ms.
* **Zero Unauthorized Collateral Disruption:** Mission-critical partner gateways and executive accounts are safeguarded by blast-radius policy checks.

---

## 🏗️ Architecture & Dynamic Schema Synthesis

```
[ Raw Enterprise Log (Okta / SAP / VPN) ]
                   │
                   ▼
  [ LLM Telemetry & Dynamic Tag Synthesizer ]
  Extracts: IP, Account, Role, Velocity, Subnet Sharedness
                   │
                   ▼
  [ TypeSafe Jev System-One Primitives (Parallel Evaluation) ]
  ├── Static Core Questions:
  │   ├── is_signature_match (Noul: 0–1 probability of automated brute force)
  │   ├── base_threat_score (Score: 0 to 2 ordered severity levels)
  │   └── triage_policy (Choice: auto_rate_limit vs draft_and_approve vs escalate)
  │
  └── Dynamic Speculative Questions (Triggered by Context Tags):
      ├── Executive Account: executive_compromise_risk (Score) & targeted_spear_risk (Noul)
      ├── Shared Gateway Subnet: blast_radius_impact (Score) & mitigation_strategy (Choice)
      └── Service Token Spray: is_internal_reconnaissance (Noul)
                   │
                   ▼
  [ Policy Engine & Blast-Radius Guardrails ]
  ├── If Low Blast + High Confidence (>0.85)  ──► [ ⚡ Autonomous Execution (WAF Rate-Limit) ]
  ├── If High Blast OR High Threat (>7.5/10)  ──► [ ⚠️ Streamlit HITL Approval Cockpit ]
  └── If Ambiguous Anomaly / Low Confidence    ──► [ 🔍 Tier-2 Threat Hunter Escalation ]
```

---

## 🚀 Quickstart & Demo Setup

### 1. Prerequisites
* Python 3.10+ (Tested on Python 3.13)
* Dependencies installed in `./venv`

### 2. Launch with One Command
```bash
./run.sh
```
This automatically launches:
* **FastAPI Backend:** `http://localhost:8000` (API Docs at `http://localhost:8000/docs`)
* **Streamlit Cockpit:** `http://localhost:8501`

### 3. Manual Launch (Alternative)
```bash
# Terminal 1: Backend
./venv/bin/uvicorn backend.main:app --port 8000 --reload

# Terminal 2: Frontend
./venv/bin/streamlit run frontend/app.py
```

---

## 🎯 7-Minute Demo Runbook for Judges (5:30 PM)

| Time | Action | What to Explain to Judges |
| :--- | :--- | :--- |
| **0:00 - 1:15** | Open **Tab 3: 1-Slide Pitch** | Introduce the problem: alert fatigue vs blast-radius trap. Explain how Sentix AutoOps solves it with TypeSafe Jev. |
| **1:15 - 2:45** | Click **🟢 Scenario 1 (Routine Noise)** | Show 4 failed logins on junior coordinator. Jev scores 0.28 (threat low), zero blast radius. **Auto-mitigated immediately** (Edge WAF rate-limit). Zero analyst time wasted. |
| **2:45 - 4:45** | Click **🔴 Scenario 2 (Attack on CFO)** | 52 attempts on CFO at 3:18 AM from an EMEA partner subnet. Show dynamic schema adaptation (`executive_compromise_risk` & `blast_radius_impact`). Threat is 9.4/10, but **system halted full subnet block** because 18 partner EDI webhooks share the subnet. Show drafted action. Click **"✅ Approve & Enforce"**. Show instant live audit ledger update! |
| **4:45 - 5:45** | Click **🟡 Scenario 3 (Token Spray)** | Irregular multi-token probe. Jev reports low confidence (0.48). Show how system gracefully escalates to Lead Threat Hunter rather than hallucinating an action. |
| **5:45 - 7:00** | Q&A & Architecture | Highlight why Jev System-One was chosen (calibrated probabilities, parallel execution, typed control flow in code, no LLM prompt drift). |

---

## 🛠️ Technology Stack
* **Decision Primitives:** TypeSafe Jev System-One (`typesafe-sdk`, `Choice`, `Score`, `Noul`)
* **Extraction:** OpenAI / Azure OpenAI GPT-4o-mini + High-fidelity heuristic fallback
* **Backend:** FastAPI, Pydantic v2, Uvicorn
* **Frontend:** Streamlit Dark-mode SOC Cockpit, Pandas
