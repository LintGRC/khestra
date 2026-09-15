# Accuracy Backlog (SKU-by-SKU)

Status: **living document.** Owner: Khestra. Last updated: 2026-08-16.

Model-independent: every item below is **open-source (OSS-tree) work**. It stands
separate from `docs/OPEN_CORE_SPLIT.md` because it has its own lifecycle (standards
revise, SKUs get marketed) and its own audience (domain authors, not platform
engineers). The split plan's §7 marketing gate says: *a framework must not be
sold as a hosted SKU until it clears the accuracy gates in this document.*

Cross-links: `docs/OPEN_CORE_SPLIT.md`, `docs/FRAMEWORK_ALIGNMENT.md`.

---

## Principles

1. **Honesty is a product requirement.** Never ship "accurate in OSS, correct in
   paid." A free catalog that is wrong and a paid catalog that is right is the
   single indefensible posture in compliance software.
2. **Collectors suggest, humans decide** — collectors never auto-pass.
3. **No legal opinions, no implied certification.** The product supports
   assessments; it does not certify.
4. Rule of thumb for content sourcing in an Apache-2.0 repo: use **faithful,
   clearly-flagged paraphrase** by default; use **verbatim** only where the
   license footing is documented (see SKU 1).

---

## Verified ground truth (as of 2026-08-16)

- **SOC 2 denominator is 61 criteria** — `OFFICIAL_TSC_COUNT = 61`
  (`apps/soc2/tests/test_catalog_titles.py:6`); criterion statements are locked
  verbatim for all 61 (`TSC_CRITERION_STATEMENTS`, `apps/soc2/core/tsc_2017_official.py`).
  (A raw key scan of that file shows 122 — each of the 61 appears in two dict
  structures; it is not 122 criteria.)
- **299 official Points of Focus titles are locked** for all 61 criteria
  (`TSC_POF_TITLES`, `apps/soc2/core/tsc_2017_official.py`) — matching the source
  exactly (`docs/trust-services-criteria-2017.txt` parses to 61 criteria / 299
  PoF bullets; source = AICPA 2017 TSC with March 2020 conforming updates — not
  the 2022 Revised PoF set). An earlier "301" count included 2 glossary entries
  scraped into `P8.1`; the extractor now stops at "Appendix A — Glossary" and
  `P8.1` carries its 6 real PoFs.
  The catalog *display layer* (`apps/soc2/core/soc2_catalog.py`) builds
  `points_of_focus` from `apps/soc2/core/soc2_pof_paraphrases.py` — complete,
  faithful paraphrases for all 299 in official order, count parity asserted per
  criterion by `apps/soc2/tests/test_catalog_titles.py::test_catalog_pof_parity_with_official`.
- **ISO 27001 clause subdivisions are now modeled, and the id collision is
  fixed.** The shared catalog (`packages/control_catalog/catalog.py`) scopes ISO
  27001 rows to `ISO27K-*` ids and adds the assessment units
  `ISO27K-6.1.1–6.1.3` / `ISO27K-9.2.1–9.2.2` / `ISO27K-9.3.1–9.3.3`; ISO 42001
  keeps its `ISO-*` ids, so the two frameworks no longer share an id space.
  `packages/refs/format.py` (+ TS mirror) render `ISO27K-*` as "ISO 27001".
- **Amd 1:2024 climate determination is a tri-state decision, not a checkbox.**
  `packages/org_context` records `climate_status` in
  `not_assessed | relevant | not_relevant` (+ justification `climate_note`),
  with the legacy `climate_relevant` bool kept as a derived convenience.
- **DC Section 200 is locked** (`apps/soc2/core/dc_200_official.py`): all 16
  criteria (DC-1.1–DC-7.1) with required/recommended flags and faithful
  paraphrases (AICPA text is copyrighted); `system_description.py` /
  `ssp_export.py` source titles + `required` from the lock.
- **Collector auto-approval was the old behavior** and is now fixed (2026-08-16):
  `review_status="approved" if check.status == "pass"` existed at 5 attach sites;
  all set to `review_status="pending"` (collectors never auto-pass). The pass/fail
  signal remains in `auto_status` for the badge; humans approve in the Evidence Hub.

---

## SKU ordering

> Close a SKU before it goes on a homepage. Order = landing priority, not
> effort order.

### SKU 0 — CMMC L2 (private pilot)

- State: pilot runs the **full monorepo** (collectors enabled). The open-core
  decoupling (Phase 1) must not block it.
- Publishable as OSS **without** waiting for SKU 1–2: CMMC L2 gaps are defended
  by the existing SPRS/validation/POA&M engines, not by SOC 2 PoF or ISO
  subclause detail.

### SKU 1 — SOC 2: Points of Focus reconcile + license gate

- **Status: DONE (2026-08-17).**
- The catalog `points_of_focus` is built from
  `apps/soc2/core/soc2_pof_paraphrases.py`: complete, faithful paraphrases of
  all 299 official PoFs in official order (61 criteria), carrying `id`/`theme`/
  `text`. `apps/soc2/tests/test_catalog_titles.py` asserts per-criterion count
  parity + ordered ids (`test_catalog_pof_parity_with_official`) and the total
  (`test_official_pof_total_is_299`).
- Licensing note: AICPA PoF titles are copyrighted; the OSS catalog ships
  paraphrases, not verbatim titles (see `docs/ACCURACY_BACKLOG.md` principles
  #4). The `tsc_2017_official.py` lock module retains the extracted titles as
  the reference the paraphrases are checked against.
- Exit met: all 61 criteria show reconciled PoFs; parity test green; licensing
  note present next to the data (`soc2_pof_paraphrases.py` docstring).

### SKU 2 — ISO 27001: clause subdivisions + id collision

- **Status: DONE (2026-08-17).**
- Assessment units added (shared catalog, `ISO27K-6.1.1`–`6.1.3`,
  `ISO27K-9.2.1`–`9.2.2`, `ISO27K-9.3.1`–`9.3.3`).
- Shared-catalog id collision fixed: ISO 27001 rows re-scoped to `ISO27K-*`;
  ISO 42001 keeps `ISO-*`. `packages/refs/format.py` (+ TS mirror) now render
  `ISO27K-*` as "ISO 27001".
- **Amd 1:2024 climate-change field:** `packages/org_context` records a
  tri-state `climate_status` (`not_assessed | relevant | not_relevant`) with a
  `climate_note` justification; legacy `climate_relevant` bool is derived for
  backward compatibility. Frontend context page exposes the tri-state control.
- Exit met: ISO 27001 catalog carries the clause subdivisions as distinct
  assessment units; no id shared with ISO 42001; parity tests green.

### SKU 3 — Labels & honesty pass

- **EU AI Act:** display "curated subset (40 of 113 articles)" wherever the
  EU framework is surfaced; never imply full-regulation coverage.
- **Collectors never auto-pass:** DONE (2026-08-16) — keep it that way; add a
  test if not covered by evidence_hub suites.
- **No legal opinion:** schemas/UI say "support for assessment," never
  "certified/guaranteed to pass."
- Escalate the `verify` CLI behavior: unreviewed auto-evidence now shows up as
  a review finding — intended ("collectors suggest, humans decide").

### SKU 4 — SOC 2 Type II wording gate

- Market "audit ready" / "Type II" **only** if the product holds tests across
  the engagement period (evidence with `period_covered` spanning the audit
  period). Otherwise drop the phrase or market Type I explicitly.

### Contextual SKU — EU AI Act depth (optional)

- EU Arts 40–41 (conformity assessment) modeled **only** if the product is
  marketed as EU AI Act compliance specifically, not as generic AI governance.
  Per FRAMEWORK_ALIGNMENT, do not invent the remaining 113 articles.

### Explicitly not on this plan

CMMC L3 UI · EU notified-body articles · collector coverage % · auto-scoring ·
ISO shall-text rendering. (Absence here is a scope decision, not a promise to
avoid.)

---

## How to work this backlog

- Items land in the **OSS tree first, before any paid SKU marketing** (§7 gate
  in OPEN_CORE_SPLIT.md).
- Each item ships with a **parity test** locking data to the official source
  module (the FRAMEWORK_ALIGNMENT pipeline pattern).
- Update "Verified ground truth" here when re-measuring; it is the source of
  accurate numbers for the split plan.