# Lucky OS — AI Startup Copilot

> Your AI co-founder for navigating Chinese company registration (工商注册) — from naming the company to estimating opening costs and matching government support policies.

Lucky OS is a bilingual (English / 中文) Vue 3 + FastAPI application that turns the dense, jargon-heavy process of registering a company in China into a guided, conversational journey. Instead of static forms and lookup tables, an **LLM-powered agent** reasons over everything the user has entered so far and produces tailored recommendations at each step.

---

## Why an Agent?

Company registration is not a fixed checklist — every decision depends on the ones before it. The kind of business you describe affects whether you need pre-approval, which shapes your recommended company type, which influences registered capital, address, org structure, opening cost, and which subsidies you qualify for.

Lucky OS treats this as a **stateful agent loop** rather than a series of disconnected forms:

- **Context accumulation** — Every step sends `formData`, the full set of fields saved so far. The agent always reasons over complete context, not just the current input.
- **Reasoning, not lookup** — Each endpoint builds a structured prompt and calls an LLM (OpenAI-compatible) that returns validated JSON. Recommendations adapt to the specific business, not a hard-coded rule tree.
- **Schema-guarded output** — Responses are forced into `json_object` mode and validated against Pydantic schemas, so the agent's free-form reasoning is safely consumed by a typed frontend.
- **Bilingual by design** — An `X-Lang` header flows from the UI into every prompt, so the agent reasons and answers in the user's chosen language with a consistent industry/approval vocabulary.

---

## Features

Lucky OS is organized into four modules (sidebar navigation):

### 📋 Registration Advisor (`reg`)
A multi-step wizard that walks a founder through company registration. Each step is an agent call:

1. **Name generation** — Suggests 3–5 valid full company names from a preferred trade name + business description, and flags pre/post-approval needs.
2. **Approval check** — Determines whether the business requires administrative approval, what type, and the details.
3. **Business scope** — Expands the declared business into a complete, compliant set of operating-scope items.
4. **Company type** — Recommends an entity type based on headcount, shareholder count, and prior answers, with reasoning.
5. **Registered capital** — Estimates a sensible capital figure (万元) for the business type and intent.
6. **Address** — Recommends an address strategy (commercial office / park-incubator / virtual / residential) given business, capital, and province.
7. **Org structure tips** — Generates guidance on organizational structure.

### 📊 Control Sandbox (`control`)
An **opening-cost estimator** that asks the agent to project first-quarter startup costs across six cost categories, returning chart-ready data and contextual tips (visualized with Chart.js).

### 🎯 Policy Engine (`policy`)
A **support-policy search** agent that matches the company profile against government incentive programs, estimating potential benefits, declaration priority, and required materials.

### ⚖️ Legal Assistant (`legal`)
A library of **high-frequency contracts and HR documents** (labor contracts, offer letters, NDAs, non-compete agreements, employee handbooks, payroll/attendance templates, and more). Download individually or as a single zip.

---

## Architecture

```
┌─────────────────────────────┐         ┌──────────────────────────────┐
│   Frontend (Vue 3 + Vite)   │  /api   │     Backend (FastAPI)        │
│                             │ ──────► │                              │
│  • Tab-based modules        │  X-Lang │  routes.py   → endpoints     │
│  • Shared reactive store    │         │  services/   → agent logic   │
│  • vue-i18n (en / zh)       │ ◄────── │  schemas.py  → validation    │
│  • apiFetch() client        │  JSON   │  prompts.py  → bilingual     │
└─────────────────────────────┘         │  llm_service → OpenAI-compat │
                                         └───────────────┬──────────────┘
                                                         │
                                                   ┌─────▼─────┐
                                                   │    LLM    │
                                                   └───────────┘
```

**Frontend** (`src/`): Vue 3 + TypeScript, no router. Navigation is tab-based via a `ref` in `App.vue`. Shared state lives in a single `reactive` store (`src/store.ts`). The `apiFetch` client (`src/api/client.ts`) auto-injects the `X-Lang` header from the active locale on every call.

**Backend** (`server/`): FastAPI app. `routes.py` exposes the agent endpoints under `/api/v1`; `services/business_service.py` builds prompts, calls the LLM, and normalizes/validates output; `services/prompts.py` holds the bilingual prompt and controlled-vocabulary definitions; `schemas.py` defines request/response models; `llm_service.py` wraps an OpenAI-compatible async client.

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- An OpenAI-compatible LLM endpoint + API key

### 1. Configure the backend

Create `server/.env`:

```bash
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
LLM_MODEL=your-model-name
```

### 2. Run the backend (FastAPI)

```bash
cd server
uv sync            # or: pip install -e .
python start.py    # serves the agent API
```

Interactive API docs are available at `/docs`.

### 3. Run the frontend (Vite dev server, port 5173)

```bash
npm install
npm run dev
```

Vite proxies `/api` to the backend.

### Build for production

```bash
npm run build      # vue-tsc -b && vite build
npm run preview
```

---

## API Overview

All agent endpoints are `POST` under `/api/v1` and accept the accumulated `formData` plus the current step's fields. They honor an `X-Lang` header (`en` | `zh`).

| Endpoint | Purpose |
|---|---|
| `/generate-names` | Suggest company names + approval flags |
| `/check-approval` | Determine approval requirements |
| `/business-scope` | Expand compliant business scope |
| `/company-type` | Recommend entity type |
| `/capital-estimate` | Estimate registered capital |
| `/address-recommendations` | Recommend address strategy |
| `/org-tips` | Org-structure guidance |
| `/opening-cost-estimate` | Project first-quarter costs |
| `/support-policies/search` | Match government incentives |
| `/documents`, `/documents/{id}/download`, `/documents/download-all` | Contract & HR templates |

Full request/response details are in [`API.md`](./API.md).

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | Vue 3, TypeScript, Vite, vue-i18n, Chart.js |
| Backend | FastAPI, Pydantic, Uvicorn |
| AI | OpenAI-compatible LLM (async, JSON-mode) |

---

*Built for the UCWS Singapore Hackathon 2026.*
