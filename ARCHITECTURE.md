# Khestra — Architecture & Master Plan

## Vision

Evidence hub collection is the central backend. All apps connect to it and work independently. The framework determines which tools are available — not every app gets every tool.

---

## Evidence Hub — The Central Backend

The `packages/` directory is the evidence hub. Every app imports the same shared packages, each instantiated with its own data directory at startup.

- **Shared code, isolated data** — same logic, separate JSON stores per app
- **Cross-framework queries** — the platform app can aggregate data from all 5 backends
- **Loose coupling** — removing an app doesn't break others; shared packages remain intact

```
packages/
  evidence/          ← File storage + collector engine (connectors: Entra, AWS, GitHub, Intune)
  exceptions/        ← Exception lifecycle (CRUD, milestones, comments, attachments, CSV/PDF)
  risks/             ← Risk register (CRUD, likelihood/impact scoring, treatment plans)
  policies/          ← Policy management (CRUD, attestations, templates, DOCX export)
  findings/          ← Audit findings (CRUD, severity, remediation tracking)
  vendors/           ← Third-party vendor management (intake, assessment, remediation)
  assets/            ← IT asset inventory
  testing/           ← Control testing records
  audit/             ← Audit trail / event log
  audit_center/      ← Audit engagement management
  remediation/       ← Remediation tracking hub
  ccf/               ← Common Control Framework (cross-framework mapping)
  orgs/              ← Organization & user management
  raci/              ← RACI role assignments
```

---

## Feature Ownership Matrix

| Feature | CMMC (NIST 800-171) | SOC 2 (AICPA) | AIGov (ISO 42001 / NIST AI RMF) |
|---------|---------------------|---------------|----------------------------------|
| **Exception Tracker** | YES — POA&M Generator (DoD format) | YES — Remediation plans | YES — Risk treatment plans |
| **Risk Register** | NO | YES — CC3.1/CC3.2 | YES — Core of AIGov |
| **Vendor Intake** | LOW — Prime boundary only | YES — CC9.2 | YES — 3rd party models/APIs |
| **Gap Analysis** | YES — SPRS self-attestation | YES — Readiness Assessment | YES — AI inventory |
| **Tabletop Exercise** | NO | YES — IR/BCP expected | YES — AI Red-teaming |
| **Audit Log** | YES | YES | YES |
| **Evidence Hub** | CORE | CORE | CORE |
| **Policy Hub** | MEDIUM — Required docs only | CORE — Annual review/attestation | CORE — Acceptable use, data gov |
| **Audit Findings** | LOW — Pass/fail assessment | YES — Management Responses | YES — Internal/Regulatory findings |
| **Periods** | NO — Point-in-time | CORE — Type II date ranges | MEDIUM — Continuous monitoring |
| **Reports** | YES — SSP, SPRS | YES — System Description, Control Matrix | YES — Model Cards, Conformity |

### Framework Summaries

**CMMC — Lean, Technical, Pass/Fail**
- Needs: Evidence Hub, Exception Tracker (POA&M), Gap Analysis, Audit Log, Policy Hub (limited), Audit Findings (limited), Reports (SSP/SPRS)
- Does NOT need: Risk Register, Tabletop Exercise, Periods, heavy Vendor Intake
- Focus: POA&M export to exact DoD format. Evidence mapping strictly to NIST 800-171 families. SPRS scoring.

**SOC 2 — Narrative, Workflow-Heavy, Periodic**
- Needs: Everything in Core + Periods (Type I/II), Policy Hub (version control + signature tracking), Risk Register, Vendor Intake (CC9.2), Tabletop Exercises
- Focus: System Description generator (DOCX wizard pulling from Risk Register, Asset Inventory, Policy Hub). 44 trust criteria with evidence mapping.

**AIGov — Risk & Lineage Driven**
- Needs: Risk Register (80% of AIGov), Vendor Intake (3rd party LLMs), Policy Hub (AI Acceptable Use), Tabletop Exercises (AI Red-teaming)
- Focus: Model Inventory & Lineage — not "do you have MFA?" but "what data was this model trained on, who has access to prompt logs, what is the fallback if it hallucinates?" Model Card generator instead of System Description.

---

## Current State

```
Platform App (unified UI, port 5173)
├── Framework Switcher (CMMC ↔ SOC 2 ↔ AI Gov ↔ ISO 27001)
├── Global Workspace pages: Dashboard, Posture, Remediation Queue, Collectors,
│   Policies, Assets, Vendors, Evidence Hub, Incidents, Audits, Audit Log
├── CMMC routes (from @cmmc)
├── SOC 2 routes (from @soc2)
├── AI Gov routes (from @aigov)
└── ISO 27001 routes (from @iso27001)
```

### The Global service (apps/core, `/api/core`)

The single home for all cross-framework services uses a **neutral namespace** —
`/api/core/*` — so it is not coupled to any framework. It is served by the
standalone `global-api` service (8086), which mounts **every shared router
exactly once**: collectors, evidence hub, personnel, policies, risks, assets,
vendors, incidents, audit log, trust center, compliance calendar,
effectiveness, control tests, remediation, exceptions, orgs, raci, ccf,
findings, audit center, training, reviews, org-context, management review,
notifications, and the shared auth routes. Framework-specific surfaces stay on
their own prefixes (`/api/cmmc`, `/api/soc2`, ...).

- The Collectors page, Remediation Queue executor, CIS posture, the Evidence
  Hub, and every global workspace page call `/api/core`.
- The shared collector store + shared evidence DB make results global across
  all frameworks regardless of which backend hosts the namespace.

All backends run from `apps/platform/run-dev.sh` (monitored, `--reload`):

| App | Port | Role |
|-----|------|------|
| CMMC API | 8081 | Controls, SPRS, SSP, POA&M, readiness (framework routes only) |
| SOC 2 API | 8082 | SOC 2 controls/periods, reports (framework routes only) |
| AI Gov API | 8083 | FRIA, model registry, governance (framework routes only) |
| ISO 27001 API | 8085 | SoA, controls, clauses (framework routes only) |
| Global API | 8086 | All shared routers, mounted once (merged platform + core) |
| Schedulers | — | Background collector scheduler daemons (separate processes) |

The legacy standalone frontends (formerly ports 5174/5175) are superseded by the
unified platform UI; `apps/cmmc/frontend` is no longer part of the main dev flow.

### What's Shared Today

- **Backend:** All shared packages (`packages/`) imported by all apps ✅
- **Frontend:** Unified UI global pages (Policies, Vendors, Assets, Evidence Hub,
  Incidents, Audits, Posture, Remediation Queue, Collectors) route through
  framework-prefixed API proxies ✅
- **Evidence collection engine:** Shared across all apps, incl. the posture engine
  (`packages/evidence/collectors/posture.py`, `GET /api/collectors/posture`) ✅
- **Collector state is shared:** all apps read/write one collectors store
  (`COLLECTORS_DATA_DIR`, default `<data_dir>/collectors`) so a single scan feeds
  every framework's posture; the cmmc backend is the collector executor host
  (scheduler + run endpoints), evidence lands in the shared hub DB ✅
  - Writes are serialized with an advisory lockfile (concurrent app processes
    can't clobber each other's check hashes / run records).
  - **Connector credentials are intentionally per-app** (`<data_dir>/connectors`):
    secrets stay scoped to the backend that configured them, while the *results*
    are shared. The Collectors page surfaces the cmmc backend's credential status.
  - Upgrading from per-app collector state? Run `scripts/merge_collector_state.py`
    once to fold legacy check hashes / monitor state into the shared store.
- **Production:** `docker-compose.prod.yml` deploys cmmc, soc2, aigov, platform,
  iso27001 + Caddy (Caddyfile.prod strips `/api/{cmmc,soc2,ai-governance,iso27001}/*`
  prefixes; UI is built into the Caddy image)

---

## API Routing Architecture

```
Platform App (port 5173)
  │
  ├── /api/cmmc/*          → proxy → CMMC backend (8081)      → /api/*
  ├── /api/soc2/*          → proxy → SOC 2 backend (8082)      → /api/*
  ├── /api/ai-governance/* → proxy → AI Gov backend (8083)     → /api/*
  ├── /api/iso27001/*      → proxy → ISO 27001 backend (8085)  → /api/*
  └── /api/* (unprefixed)  → proxy → Global backend (8086)

Shared packages mount at /api/* **only on the Global backend** (8086):
  /api/exceptions/*        ← packages/exceptions/routes.py
  /api/risks/*             ← packages/risks/routes.py
  /api/policies/*          ← packages/policies/routes.py
  /api/findings/*          ← packages/findings/routes.py
  /api/vendors/*           ← packages/vendors/routes.py
  /api/assets/*            ← packages/assets/routes.py
  /api/collectors/*        ← packages/evidence/collectors/routes.py
  ...etc
```

`apiUrl()` in `shared/frontend/apiPrefix.ts` routes every shared-entity path
to `/api/core` regardless of the active framework shell, so any shared
frontend module works everywhere and each shared router answers in exactly
one place.

---

## Implementation Plan

Legend: 🔴 Must-have | 🟡 Should-have | 🟢 Nice-to-have

### Phase 1: Wire Shared Frontends per Feature Matrix

| Feature | Priority | Status |
|---------|----------|--------|
| **Exception Tracker** — All 3 (CMMC as POA&M) | 🔴 | ✅ Shared module done. Needs CMMC POA&M wrapper |
| **Risk Register** — SOC2 + AIGov only (NOT CMMC) | 🔴 | ✅ Shared module done. Wire into AIGov |
| **Policy Management** — All 3 | 🔴 | ✅ Shared module done. Wire into CMMC + AIGov |
| **Audit Findings** — SOC2 + AIGov (CMMC = LOW) | 🟡 | ✅ Shared module done. Wire into AIGov |
| **Vendor Management** — SOC2 + AIGov (CMMC = LOW) | 🟡 | ✅ Shared module done. Wire into SOC2 |
| **Gap Analysis** — All 3 | 🔴 | ✅ Shared module done. Wire into SOC2 + CMMC |

### Phase 1b: Dynamic Sidebar per Feature Flags

| Feature | Priority | Status |
|---------|----------|--------|
| Sidebar config per framework (Global Workspace visible only when SOC2/AIGov enabled) | 🔴 | Not started |
| CMMC-only sidebar (Dashboard, Org, Controls, Readiness, Export) | 🔴 | Not started |
| Scope switcher inside Evidence Hub and Exception Tracker pages | 🟡 | Not started |
| Cross-framework mapping toggle (show which frameworks use each piece of evidence) | 🟢 | Not started |

### Phase 2: Framework-Specific Features

**CMMC — Lean, Technical, Pass/Fail**

No standalone Policies, Vendors, or Assets pages. These are handled inline:
- Policies → file upload inside Controls
- Subcontractors → simple table inside Organization
- Employees → checkbox inside Controls

| Feature | Priority | Status |
|---------|----------|--------|
| POA&M Generator + Gap Analysis merged into single Readiness page (DoD-format export) | 🔴 | Not started |

**SOC 2 — Narrative, Workflow-Heavy, Periodic**

| Feature | Priority | Status |
|---------|----------|--------|
| System Description DOCX wizard (pulls from Risk Register, Asset Inventory, Policy Hub) | 🔴 | Not started |
| Vendor Intake full flow (magic-link, SOC2 upload prefill, vagueness detection) | 🔴 | Not started |
| Systems / Assets page (IT infrastructure inventory, cross-framework) | 🔴 | Not started |
| Team / Employees page (compliance status tracker — training, policy signing, background checks) | 🔴 | Not started |
| Audit Log page (immutable system mutation log, separate from audit management) | 🔴 | Not started |
| Periods (Type I vs Type II date pickers, freeze/unfreeze) | 🟡 | Complete |
| Policy Hub version control + employee signature tracking | 🟡 | Not started |
| Wire shared Vendor Manager | 🟡 | Ready to wire |
| Tabletop Exercises (IR/BCP scenarios) | 🟢 | Not started |

**AIGov — Risk & Lineage Driven**

| Feature | Priority | Status |
|---------|----------|--------|
| Model Card generator (instead of System Description) | 🔴 | Not started |
| Team / Employees page (AI training + acceptable use policy signing) | 🔴 | Not started |
| Wire shared Risk Register (80% of AIGov) | 🟡 | Ready to wire |
| Wire shared Policy Hub (AI Acceptable Use, data governance) | 🟡 | Ready to wire |
| Vendor intake for 3rd party LLMs (magic-link, SOC2 prefill) | 🟡 | Complete |
| Incident templates + bulk ops + blast radius | 🟡 | ✅ Done |
| Wire shared Audit Findings | 🟡 | Ready to wire |
| Tabletop Exercises (AI Red-teaming scenarios) | 🟡 | Complete |
| FRIA comparison page (side-by-side) | 🟡 | Not started |
| FRIA risk heatmap | 🟡 | Not started |
| FRIA "mine only" filter | 🟢 | Not started |
| Per-model governance score | 🟢 | Not started |

### Phase 3: Universal Core (All 3 Frameworks)

| Feature | Priority | Status |
|---------|----------|--------|
| Evidence Hub | 🔴 | ✅ Complete |
| Audit Log (immutable) | 🔴 | ✅ Backend shared |
| Systems / Assets page (cross-framework inventory) | 🔴 | ✅ AIGov done (Systems). Needs SOC2 + CMMC pages |
| Team / Employees page (compliance status tracker) | 🔴 | Not started |
| Gap Analysis UI | 🔴 | ✅ Shared module done |
| Exception Tracker POA&M | 🔴 | ✅ Shared module done |
| Fix `--border-color` → `--border` in Findings.tsx, ExceptionPanel.tsx, FindingPanel.tsx, RiskPanel.tsx | 🟡 | Not started |
| Cross-framework evidence search | 🟢 | Not started |
| Unified exception view across frameworks | 🟢 | Not started |
| CCF Mapping UI (visual control mapping) | 🟢 | Not started |

### Phase 4: Housekeeping

| Task | Priority | Status |
|------|----------|--------|
| AI Gov standalone frontend — populate `apps/aigovernance/frontend/` or remove scaffold | 🟡 | Not started |
| Export CSV from Governance Dashboard | 🟡 | Not started |
| Evidence freshness indicators in Governance Dashboard | 🟡 | Not started |

---

## Sidebar & Navigation Design

Three-layer sidebar. The Active Framework section is dynamic — it changes based on which framework is selected and which features that framework requires.

### SOC 2 Sidebar (Continuous Management Engine)

```
GLOBAL WORKSPACE
├── Dashboard
├── Policies
├── Vendors
├── Team
└── Audit Log

SOC 2 Type II ▾
├── Controls
├── Risk Register
├── Evidence Hub (16)
├── Evidence Requests (1)
├── Exceptions (1)
├── Findings (1)
└── Reports

SETTINGS
├── Workspace
└── Integrations
```

### AIGov Sidebar (Continuous Management Engine — same structure, different vocabulary)

```
GLOBAL WORKSPACE
├── Dashboard
├── Policies
├── Vendors
├── Systems
├── Team
└── Audit Log

AI Governance ▾
├── Incidents
├── FRIA
├── Risk Register
├── Exceptions
├── Gap Analysis
├── Findings
└── Tabletop

SETTINGS
├── Workspace
├── Integrations
└── Help & FAQ
```

### CMMC-Only View

---
CMMC is a point-in-time technical assessment. It doesn't need the heavy Global Workspace. Policies, vendors, and assets shrink down and merge into the CMMC-specific tabs.

```
ACTIVE FRAMEWORK
  [ CMMC Level 2 ▾ ]
    Dashboard             ← SPRS score, readiness %
    Organization          ← System boundary, SSP narrative
    Controls              ← NIST 800-171 families with evidence uploads
    Readiness & POA&M     ← Gap analysis + exceptions
    Export                ← SPR, SSP, POA&M to DoD formats

SETTINGS
  Workspace Settings
```

Where did the "Global" items go?
- **Policies** → uploaded as evidence directly inside the relevant Control (e.g. upload IR policy inside Control 3.6.1)
- **Vendors (subcontractors)** → a simple table inside the Organization tab for SSP generation
- **Employees** → checkboxes inside Controls (e.g. Control 3.9.1 for background checks)
- **Audit Log** → Settings (optional for CMMC-only customers)

### Key Design Decisions

- **Systems/Assets** lives in Global Workspace because an AWS EC2 instance or AI model may be in-scope for multiple frameworks. Inside a framework context, scope filters show which systems apply.
- **Settings & Integrations** are workspace-wide (AWS integration applies to all frameworks, not just SOC2). Always at the bottom as a distinct section.
- **Audit Log** (who changed what) is Global Workspace. Audit management (controlling auditor access, report requests) stays framework-specific.
- **Team/Employees** is a lightweight compliance status tracker (training, policy signing, background checks) — not a full HR system.
- **SOC2 and AIGov share the same sidebar structure** (Global Workspace + Active Framework + Settings). Only the Active Framework items and vocabulary differ.
- **CMMC is the outlier** — it strips the Global Workspace entirely and handles policies/vendors/employees inline inside Controls and Organization.

### Scope Switcher (Power-User Feature)
Inside Evidence Hub and Exception Tracker pages, a first-class scope indicator lets advanced users reveal cross-framework mappings:

```
Evidence Hub
Scope: [ SOC 2 ▾ ]

[Toggle: Show cross-framework mappings]
```

When toggled:

```
AWS IAM Screenshot
Used by:
✓ SOC 2 (CC6.1)
✓ CMMC (3.1.1)
✓ ISO 42001 (Clause 7.2)
```

The scope switcher is the platform's differentiator — "Write Once, Satisfy Many" — without confusing new users.

---

### Global Policy Hub — Cross-Framework Mapping

Policies are **company resources**, not framework resources. One Global Policy Hub in Global Workspace. Frameworks consume policies via mappings.

#### How it works

A single corporate policy satisfies requirements across multiple frameworks:

```
Information Security Policy  v3.2  [Approved]
│
├── ✓ SOC 2  ──> CC1.2, CC6.1, CC6.2
├── ✓ CMMC   ──> AC.L2-3.1.1
├── ✓ AIGov  ──> Section 7.4 (System Access Controls)
└── ✓ ISO 42001  ──> Clause 8.3
```

The policy exists once. The mappings exist many times.

#### Policy Dashboard — Mapping Panel

When a user opens a policy in the Global Hub, a **Cross-Framework Mapping** panel shows coverage:

```
🔒 Policy: Access Control & Password Policy
──────────────────────────────────────────────────────────
[ Document Content / Editor ]
...

🗺️ Cross-Framework Mappings:
  Status  │ Framework  │ Controls
  ────────┼────────────┼──────────────────────────────
  ✓       │ SOC 2      │ CC6.1 (Access Controls), CC6.2 (User ID)
  ✓       │ CMMC       │ AC.L2-3.1.1 (Limit Authorized Users)
  ⚠       │ AIGov      │ No mapping — add mapping
  ✓       │ ISO 42001  │ Clause 8.3

[ Add Mapping ] [ Bulk Map ]
```

Users can add/remove mappings per framework. The mapping panel is a table: Framework dropdown → Control/Clause selector → Save.

#### How framework contexts pull policies in

When a user is inside **SOC 2** → **Controls** → **CC6.1**, the control detail page shows:

```
Required Policies
✓  Access Control Policy (mapped)
✓  Information Security Policy (mapped)
⚠  Incident Response Policy (not yet mapped — link to Global Hub)
```

Clicking a policy takes the user to the Global Policy Hub (opens in same tab or side panel). The user never creates a policy from inside a framework context — they map existing ones.

#### The policy list filter

The Policy Dashboard also supports filtering by framework:

```
[ All Policies ▾ ]  [ Add Policy ]
│
├── Access Control Policy     ── Used by: SOC2, CMMC
├── AI Acceptable Use Policy  ── Used by: AIGov
├── CUI Handling Procedure    ── Used by: CMMC
└── Data Retention Policy     ── Used by: SOC2, AIGov
```

Filter by framework to see which policies apply (or are missing) for a given program.

#### Data model

The backend already has `packages/policies/` with a shared policy model. The mapping table lives alongside it:

```python
# packages/policies/store.py
# Each policy_mapping record:
{
  "policy_id": "pol_abc123",
  "framework": "soc2",
  "control_id": "CC6.1",        # or CMMC control ref, AIGov clause
  "mapped_at": "2026-06-30T..."
}
```

No new backend package needed — just a new collection in the existing store.

#### What to build

| Piece | Status |
|-------|--------|
| Backend: `GET /api/policies/{id}/mappings` | Not started |
| Backend: `POST /api/policies/{id}/mappings` (add mapping) | Not started |
| Backend: `DELETE /api/policies/{id}/mappings/{mid}` | Not started |
| Frontend: Mapping panel in Policy Dashboard detail view | Not started |
| Frontend: Framework filter dropdown in Policy list | Not started |
| Frontend: Control page shows "Required Policies" with links to Global Hub | Not started |

#### Same pattern applies to other global resources

The same cross-framework mapping concept applies to:
- **Evidence** — "AWS IAM Screenshot" satisfies SOC2 CC6.1 + CMMC 3.1.1
- **Exceptions** — One exception can span multiple frameworks
- **Vendors** — One vendor assessment can be used by SOC2 and AIGov
- **Assets** — One AWS EC2 instance can be in-scope for SOC2 + CMMC

Each gets a scope switcher and a "Used by" panel. Build the pattern once in the Policy Hub, then replicate.

### Implementation: Dynamic Sidebars via Feature Flags

The sidebar is not static. It renders based on the customer's `frameworks_enabled` array.

```typescript
// Pseudocode for sidebar configuration
const sidebarConfig = {
  globalWorkspace: {
    visible: frameworks.length > 1 || frameworks.includes("SOC2") || frameworks.includes("AIGov"),
    items: [
      { label: "Dashboard", path: "/dashboard" },
      { label: "Policies", path: "/policies", engine: "full" },  // SOC2/AIGov get full engine
      { label: "Vendors", path: "/vendors", engine: "full" },
      { label: "Assets & Employees", path: "/assets" },
      { label: "Audit Log", path: "/audit-log" },
    ],
  },
  activeFramework: {
    type: frameworks[0], // "SOC2" | "CMMC" | "AIGov"
    items: getFrameworkNav(frameworks[0]), // Different nav per framework
  },
};
```

CMMC-only: Global Workspace hidden. Controls page renders `<SimpleFileUpload />` for policies instead of `<PolicyWorkflowEngine />`.
SOC2/AIGov: Global Workspace visible with full workflow engines.

---

## Key Principles

1. **Backend is the source of truth** — all data lives in `packages/*/store.py` with JSON file persistence
2. **Frontend is a view layer** — shared modules adapt to the active framework via API prefix
3. **Framework dictates tooling** — not every app gets every tool. The feature matrix is the authority.
4. **App removal is safe** — removing an app only removes its specific routes; shared packages remain
5. **No cross-app data coupling** — each app has its own data directory; the platform app aggregates via API calls

---

## Implementation Guidelines

### Do
- Build Exception Tracker, Evidence Collection, Gap Analysis, and Audit Log as universal core (all 3 frameworks)
- Build Risk Register, Vendor Intake, Tabletop Exercises as SOC2 + AIGov only
- Tag all framework-specific config (risk vectors, control mappings, asset types) per framework
- Keep CMMC lean — point-in-time, pass/fail, POA&M export to DoD format
- Make SOC 2 heavy — narrative workflows, periods, signature tracking, System Description DOCX
- Make AIGov about risk and lineage — Model Cards, FRIA, incident lifecycle
- Use dynamic sidebars via feature flags — CMMC-only hides Global Workspace
- Present evidence, exceptions, gap analysis inside the active framework context (never expose "shared component" labels)
- Make scope a first-class UI concept inside shared tool pages (Evidence Hub, Exception Tracker)
- Use the same API patterns for CRUD operations across all three apps

### Don't
- Force Risk Register or Tabletop Exercises into CMMC (confuses users, bloats UI)
- Build Periods for CMMC (point-in-time, no type I/II)
- Duplicate evidence connectors per framework
- Hardcode framework-specific fields into shared data models
- Treat AI risk vectors as optional metadata — they are first-class fields
- Expose backend architecture in the sidebar (no "Shared Utilities" sections)
- Organize UI around backend services — organize around user mental models

---

## Competitive Advantage

By overlaying AI governance onto existing SOC 2 and CMMC core, the platform can tell enterprise buyers:
> "You don't need a separate tool for AI risk. Your exceptions, vendor reviews, and automated evidence dossiers all live in the exact same secure repository your team already uses for corporate compliance."

This eliminates:
- Duplicate vendor assessments
- Siloed risk registers
- Manual evidence forwarding between compliance tools
- Separate audit timelines for AI versus traditional GRC

---

## the tools in AI gov app came from tools/postureai but ported over (it may be incomplete)

---

## Global service consolidation (roadmap)

Phase 1 (done): prod compose shares all global entity DBs (`RISKS`, `VENDOR`,
`ASSETS`, `INCIDENTS`, `REVIEWS`, `PERSONNEL`, `AUDIT_LOG` + existing
`AUTH`/`POLICIES`/`EVIDENCE`/`COLLECTORS`) on the `shared_auth` volume —
dev/prod parity for the global data tier.

Phase 2 (done): `/api/core` neutral namespace in the unified UI + Vite/Caddy.

Phase 3 (done): `apps/core` — a standalone FastAPI service (port 8086)
hosting the shared routers under `/api/core/*`, with JWT auth against the
shared auth DB and a generic attach layer using `CHECK_TO_FRAMEWORKS`.
Caddy routes `/api/core` + `/api/evidence-hub` to it.

Phase 4 (done, then superseded): shared routers stayed mounted on framework
backends as a "framework lens". Removed in the consolidation — every shared
router now mounts **only** on the Global service.

Phase 5 (done): **platform + core merged into one Global app**
(`apps/core/server/main.py`, `FastAPI(title="Khestra Global")`, compose
service `global-api`). The former platform app (personnel, trust center,
compliance calendar, effectiveness, control tests, auth routes) folded in;
`apps/platform` retired. Framework apps (cmmc/soc2/aigov/iso) serve only
their own framework routes. `shared/frontend/apiPrefix.ts` routes every
shared-entity path to `/api/core` from any shell. Caddy/Vite point
`/api/settings`, `/api/personnel`, `/api/trust-center` at the Global service.
Security hardening: one auth middleware, one set of security headers for the
whole shared surface.

Decision log: `/api/core` chosen over `/api/evidence` because the namespace
hosts all core entities (collectors, evidence, policies, risks, assets,
vendors, incidents) — "evidence" would be too narrow. Core endpoints use
shared-auth JWTs (user identity + tenant + RBAC + audit); service-to-service
calls use scoped internal tokens only if needed.
