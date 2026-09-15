# SSP Narrative User Workflow

## Overview

A single unified pipeline for generating SSP implementation narratives. The user
fills out org context, collects evidence, and clicks one button to generate the
best possible draft — then reviews, edits, and approves.

---

## Step 1 — One-time org setup

User fills out two forms:

**Org profile** — System name, owner, boundary, address, ISO name, team roster.
**Environment scope** — M365 yes/no, cloud provider (Azure/AWS/none), remote
workforce, wireless, mobile devices, CUI processing.

Takes 2-3 minutes. Done once per assessment.

---

## Step 2 — Collect evidence

Three ways (can mix):

| Method | What happens | Result |
|--------|-------------|--------|
| **Automated collector** | User runs a connector (Entra, AWS) | `collector_*` JSON artifacts attached per-control |
| **Manual upload** | User drags a PDF/config export onto a control | Evidence file attached |
| **Skip** | No evidence for this control | Generation still works — uses starter + inheritance |

Collectors can be scheduled or run on-demand. Manual upload always available.

---

## Step 3 — Generate narrative (one control)

User clicks **"Generate"** on a control detail page. One click does all this:

```
Org profile  ──┐
Env scope   ──┤
Evidence    ──┼──► Merge into draft
Inheritance ──┤
Starter     ──┘
                    │
                    ▼
          Optional AI polish
          (user checked "use AI")
                    │
                    ▼
          Draft appears in textarea
          with source badges:
          [Org] [2 evidence files] [Inheritance] [AI]
```

**Rules for existing narratives:**

- Empty → generate from scratch (all sources)
- Auto-generated (no manual edit) → append new evidence findings
- Human-edited → nothing changes unless user clicks "Regenerate"

---

## Step 4 — Manual optimize + approve

User reads the draft in the textarea:

- **Edit freely** — type changes, reword, add missing context
- **Remove AI fluff** — if AI added generic filler
- **Add specifics** — names, dates, ticket numbers

When satisfied: **click Save**. This marks the narrative as `human_edited =
true` so future generate calls won't overwrite it.

---

## Step 5 — Bulk generate (optional shortcut)

Instead of per-control, user clicks **"Generate all"** with scope:

- `missing_met` (safest — controls marked MET but empty narrative)
- `all_empty` (all controls with no narrative)
- `all` (overwrite everything — requires confirmation)

AI can be toggled off to save tokens/cost. Each control follows the same
internal pipeline. User then reviews controls one by one, edits, saves.

---

## Complete lifecycle of one control narrative

```
Org setup → Collectors run → Generate → Review → Edit → Save
                                 ↑
                          Regenerate available
                          (resets human_edited flag)
```

**Retired:** "Apply starter", "AI suggestion modal", "Append vs Replace" toggles
— all replaced by one "Generate" button per control.

---

## Control detail page wizard order

The wizard on a single control page follows this linear flow:

1. **Status** — Assessment status (MET / NOT MET / etc.) and maturity dropdown
2. **Evidence** — Upload files, run automated collectors, view attached artifacts
3. **Describe** — Click "Generate" to produce a narrative from evidence + org
   profile + starter + optional AI polish. Edit freely, then Save
4. **Fix plan** — POA&M fields (remediation plan, owner, target date, cost).
   Only shown when status is a gap (NOT MET / PARTIALLY MET / PLANNED)

This replaces the old order (Status → Describe → Evidence → Fix plan) where
you had to write the narrative before uploading evidence.

---

## Source annotations

After generation, the UI shows source badges so the user knows what data was
used:

```
[✅ Org profile] [✅ 3 evidence artifacts] [⚠️ Inheritance: partial] [✅ AI polish]
```

Helps user trust (or distrust) the generated text and know what to fact-check.

---

## Key invariants

1. All writes go through `patch_control()` — single gateway
2. `human_edited` flag prevents accidental overwrite
3. AI only polishes, never adds facts not supported by evidence or starter
4. Bulk generate only touches empty or auto-generated narratives
