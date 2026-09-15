# Cross-Framework Platform Considerations

## 1. The Shared Core (70% Overlap)

SOC 2, CMMC, and AI Governance share the same operational workflows. These should be built as framework-agnostic services, not duplicated per app.

### Exception Tracker
Fully transferable. Whether the asset is an S3 bucket, a legacy server, or an unvetted LLM — the workflow is identical:
- **Risk Assessment**: Likelihood × Impact scoring
- **Executive Sign-off**: Approval gate before expiry
- **Expiration Date**: Auto-revoke or extend
- **Mitigation Controls**: Compensating controls attached to each exception

**Rule**: The Exception data model must be framework-agnostic. Only the risk vector labels change per framework.

### Evidence Collection Engine
The background service that catches state transitions, compiles report PDFs, cryptographically hashes them, and bundles dossiers works identically across all three:
- Trigger event → log entry → tie to asset ID → store securely
- Frameworks don't care if the event is `MFA_ENFORCED_ON_GITHUB`, `SSP_UPDATED`, or `FRIA_SNAPSHOT_APPROVED`
- Collector connectors (Entra ID, AWS, GitHub, Intune) are already framework-agnostic in `packages/evidence/`

**Rule**: Evidence collectors are pure connectors. Mapping to control IDs happens in a per-framework `mapping.py`.

### Vendor Intake
A vendor intake engine that parses SOC 2 reports for SaaS vendors can be extended to parse:
- AI provider dynamic risk profiles (OpenAI, Anthropic, etc.)
- Model safety sheets
- ISO 42001 certifications

**Rule**: Vendor assessment criteria are framework-tagged. The intake pipeline is shared.

---

## 2. The Branch Points (30% Mutation)

You cannot treat an AI system like a static server asset. Three dimensions must diverge:

### A. Asset Typing — Systems vs. Infrastructure

| Dimension | SOC 2 / CMMC | AI Governance |
|-----------|-------------|---------------|
| Asset inventory | Laptops, databases, firewalls | AI Systems (e.g. "Resume Screening Tool") |
| Evidence types | Technical state checks (`port 22 open?`) | Behavioral & process-driven (system prompt, human-in-the-loop owner) |

**Consideration**: AI System registry needs its own data model with fields for model version, data lineage, deployment environment, and human oversight configuration. A static server model won't fit.

### B. Evidence Trigger Frequency

| Trigger type | SOC 2 / CMMC | AI Governance |
|-------------|-------------|---------------|
| Typical cadence | Periodic (30-day user list pull) or continuous-static (bucket public alert) | Lifecycle-dependent, event-driven |
| When evidence fires | Time interval or config drift | Prompt change, model version bump, data lineage update |

**Consideration**: Evidence scheduling must support lifecycle hooks, not just time-based or drift-based triggers. A `model_updated` event should cascade to re-collection of applicable evidence.

### C. Risk Vector Definitions

SOC 2 risk matrices calculate data breach probability. AI governance adds net-new vectors required by ISO 42001 and NIST AI RMF:

- Algorithmic bias / discrimination potential
- Intellectual property / training data copyright risk
- Model drift and hallucinations
- Data privacy guardrail compliance
- Human-in-the-loop sufficiency

**Consideration**: Risk scoring models must be polymorphic per framework. The core Likelihood × Impact engine is shared; the vector definitions are framework-specific.

---

## 3. Cross-Framework Architecture

```
                    ┌──────────────────────────────────────────┐
                    │        Unified GRC Engine                │
                    │  (Evidence Collector, Exception Logs,    │
                    │   Vendor Intake, Dossier Builder)        │
                    └───────────────────┬──────────────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            ▼                           ▼                           ▼
      [ SOC 2 Panel ]            [ CMMC Panel ]              [ AI Gov Panel ]
     - Trust Criteria           - SPRS Calculator           - System Registry
     - IAM & Cloud Checks       - SSP Generator             - FRIA Workflows
     - Static Infrastructure    - DFARS Overlays            - Lifecycle Timelines
                                - POA&M Export              - Model Card PDF
                                - Readiness Review          - AI Risk Matrix
```

**Key insight**: Each panel is additive. A CMMC-only customer sees CMMC. Add AI Gov and the Exception Tracker is already populated. The shared engine does not change — only the data model views and risk vector definitions extend.

---

## 4. Implementation Guidelines

### Do
- Build Exception Tracker, Evidence Collection, and Vendor Intake as shared `packages/` modules
- Tag all framework-specific config (risk vectors, control mappings, asset types) per framework
- Use the same API patterns for CRUD operations across all three apps
- Share the frontend sidebar, topbar, and layout shell

### Don't
- Duplicate evidence connectors per framework
- Hardcode framework-specific fields into shared data models
- Assume all assets are servers or static infrastructure
- Treat AI risk vectors as optional metadata — they are first-class fields

---

## 5. Competitive Advantage

By overlaying AI governance onto existing SOC 2 and CMMC core, the platform can tell enterprise buyers:
> "You don't need a separate tool for AI risk. Your exceptions, vendor reviews, and automated evidence dossiers all live in the exact same secure repository your team already uses for corporate compliance."

This eliminates:
- Duplicate vendor assessments
- Siloed risk registers
- Manual evidence forwarding between compliance tools
- Separate audit timelines for AI versus traditional GRC
