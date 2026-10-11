# Home Credit LAP AI Voice Agent

**Production-Minded AI Voice Agent & Qualification Engine for Home Credit Loan Against Property (LAP)**

---

## 1. Executive Summary

This project implements a complete, telephony-ready conversational AI voice qualification system for **Home Credit India's Loan Against Property (LAP)** product. It combines a production-grade System Prompt, a deterministic eligibility engine, an out-of-order conversational fact extractor, an interactive React/Vite testing dashboard, and voice platform adapters for **Retell AI** and **Bolna**.

### Key Highlights
- **100% Automated Test Coverage:** 100 out of 100 tests passing in pytest (unit, API, normalizers, edge cases, and multi-turn synthetic conversations).
- **Deterministic Qualification Gate:** Enforces all mandatory credit rules (property types, documents, income mode, loan limits, tenure range) without relying on probabilistic LLM outputs.
- **Out-of-Order Extraction:** Gracefully extracts multiple facts from single utterances (e.g. *"It's my residential house worth 1.5 Cr and I need 60 Lakhs"*).
- **Seamless Transfer Routing:** Detects existing property loan balance transfer and EMI reduction requests at any turn and routes to specialist desks.
- **₹75 Lakh Alternative Flow:** Detects loan requests exceeding ₹75L, explains the limit, and requires explicit customer consent before proceeding.
- **Interactive Testing Dashboard:** Full React 18 + Vite interface with live simulation, 7-Point Checklist tracking, Engine State Inspector, Scenario Runner, and Transcript Exporter.
- **Telephony Adapter Layer:** Modular integration for Retell AI and Bolna with HMAC-SHA256 signature verification.

---

## 2. Project Architecture & Directory Layout

```
Home Credit LAP Voice Agent/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application & middleware
│   │   ├── config.py                   # Pydantic Settings
│   │   ├── models/
│   │   │   ├── qualification.py        # Domain models, Enums, Checklist items
│   │   │   ├── conversation.py         # Session messages and schemas
│   │   │   └── voice_payloads.py       # Webhook request/response models
│   │   ├── qualification/
│   │   │   ├── rules.py                # Policy limits & disqualification rules
│   │   │   ├── normalizers.py          # Indian notation & currency parsers
│   │   │   ├── extractor.py            # Conversational fact extractor
│   │   │   └── engine.py               # Deterministic qualification engine
│   │   ├── services/
│   │   │   ├── conversation_service.py # Dialog orchestrator & prompt renderer
│   │   │   ├── simulator_service.py    # Synthetic scenario execution engine
│   │   │   └── rag_service.py          # Grounded FAQ knowledge service
│   │   ├── voice/
│   │   │   ├── adapter_base.py         # Voice platform abstract base class
│   │   │   ├── retell_adapter.py       # Retell AI schema export & webhook mapper
│   │   │   ├── bolna_adapter.py        # Bolna voice engine adapter
│   │   │   └── webhook_verifier.py     # HMAC-SHA256 signature verifier
│   │   └── api/
│   │       ├── health.py               # Health check endpoint
│   │       ├── conversation.py         # Live simulation dialog endpoints
│   │       ├── simulator.py            # Predefined test scenario endpoints
│   │       ├── voice.py                # Webhooks & agent export endpoints
│   │       └── router.py               # Central API router
│   ├── tests/                          # 100 automated pytest test cases
│   └── requirements.txt                # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx              # System status & provider badge
│   │   │   ├── CallSimulator.jsx       # Interactive voice simulation chat
│   │   │   ├── ChecklistStatus.jsx     # 7-Point Checklist visual tracking
│   │   │   ├── StateInspector.jsx      # Engine lifecycle & handoff gate monitor
│   │   │   ├── ScenarioRunner.jsx      # Multi-turn test scenario runner
│   │   │   ├── TranscriptViewer.jsx    # Formatted transcript & export (JSON/TXT)
│   │   │   └── VoiceProviderPanel.jsx  # Retell/Bolna configuration & schemas
│   │   ├── App.jsx                     # Main application layout
│   │   ├── api.js                      # Backend API client
│   │   └── index.css                   # Custom design system & glassmorphism
│   ├── package.json
│   └── vite.config.js
├── prompts/
│   ├── home_credit_lap_system_prompt.txt # Production copy-ready System Prompt
│   ├── retell_agent_schema.json          # Platform-ready Retell AI agent schema
│   └── README.md                         # Prompt variable specifications
├── scenarios/
│   ├── eligible_customer.json            # Eligible customer test journeys
│   ├── disqualification_cases.json       # Agri land, cash income, tenure exits
│   ├── transfer_cases.json               # Balance transfer & busy customer exits
│   └── edge_cases.json                   # 75L cap agreement, interruptions, corrections
├── scripts/
│   ├── run_all_tests.py                  # Automated test runner script
│   ├── test_call_simulator.py            # Interactive CLI voice simulator
│   └── export_retell_agent.py            # Retell agent exporter script
├── docs/
│   ├── ARCHITECTURE.md                   # System architecture & Mermaid diagrams
│   ├── BUSINESS_RULES.md                 # Detailed lending policy specification
│   ├── TEST_REPORT.md                    # 100-test verification report (Levels 1-6)
│   ├── VOICE_PLATFORM_SETUP.md           # Retell AI & Bolna configuration guide
│   └── GITHUB_SETUP.md                   # Safe GitHub delivery instructions
├── .env.example                          # Environment variable template
├── .gitignore                            # Comprehensive exclusions
└── README.md                             # This documentation
```

---

## 3. Prerequisites

- **Operating System:** Windows 10/11
- **Python:** 3.11+ (Tested on Python 3.13.3)
- **Node.js:** v18+ (Tested on Node v22.14.0, npm 10.9.2)
- **Git:** Git for Windows (version 2.50+)

---

## 4. Quickstart & Installation (Windows PowerShell)

Open PowerShell in the project directory: `c:\Users\manip\Desktop\Home Credit LAP Voice Agent`

### Step 1: Set Up Backend Virtual Environment
```powershell
# Create Python virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\Activate.ps1

# Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

### Step 2: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### Step 3: Configure Environment Variables
Copy the example environment template:
```powershell
Copy-Item .env.example .env
```
*(The system runs 100% locally out-of-the-box without requiring live third-party keys).*

---

## 5. Running the Application

### Option A: Start the FastAPI Backend
In your activated PowerShell terminal:
```powershell
.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Option B: Start the React Frontend Dashboard
In a second PowerShell terminal:
```powershell
cd frontend
npm run dev
```
Open your browser at: **[http://localhost:5173](http://localhost:5173)**

---

## 6. Running Tests & Automated Scenarios

### Run All 100 Tests (Pytest)
```powershell
.venv\Scripts\python scripts\run_all_tests.py
```
Or directly:
```powershell
.venv\Scripts\pytest -v backend\tests
```

### Run the Interactive CLI Call Simulator
```powershell
.venv\Scripts\python scripts\test_call_simulator.py
```

### Export Retell AI Platform Schema
```powershell
.venv\Scripts\python scripts\export_retell_agent.py
```

---

## 7. 7-Point Qualification Checklist Matrix

| # | Checklist Item | Eligible Criteria | Immediate Disqualification Rule |
|---|---|---|---|
| 1 | **Property Type** | Residential, Commercial, Industrial | **Agricultural property is strictly ineligible.** Call ends immediately. |
| 2 | **Ownership Status** | Sole OR Joint ownership | Both are eligible. Joint ownership is never rejected. |
| 3 | **Original Documents** | Original title deeds must be available | Missing/lost/disputed documents -> Immediate exit. |
| 4 | **Requested Amount** | ≤ ₹75,00,000 (75 Lakhs) | > ₹75L requires explicit customer agreement to the ₹75L cap. |
| 5 | **Occupation & Income** | Salaried / Self-Employed with Bank credit | **Cash income is strictly ineligible.** Immediate exit. |
| 6 | **Current Market Value** | Customer's estimated valuation in INR | Recorded without arbitrary minimums. |
| 7 | **Repayment Tenure** | 3 to 15 years inclusive | Tenures < 3 years or > 15 years -> Immediate exit. |

---

## 8. Voice Telephony Setup (Retell AI & Bolna)

For instructions on configuring Retell AI or Bolna, selecting Indian voices (`11labs-Pooja`), configuring webhooks, and recording calls, see [`docs/VOICE_PLATFORM_SETUP.md`](./docs/VOICE_PLATFORM_SETUP.md).

---

## 9. GitHub Repository & Delivery

- **Repository URL:** [https://github.com/Manipalsai/Home-Credit-LAP-Voice-Agent](https://github.com/Manipalsai/Home-Credit-LAP-Voice-Agent)
- **Default Branch:** `main`
- **Documentation Guide:** [`docs/GITHUB_SETUP.md`](./docs/GITHUB_SETUP.md)
