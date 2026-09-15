# Plan: Tier 1 — Style Consistency (Accuracy + Security)

Scope: fix the accuracy and security inconsistencies found in the fleet-wide style audit.
Tier 2 (conventions) and Tier 3 (structure) are intentionally out of scope.

## 1. Canonical ref format via shared renderer

- New `packages/refs/format.py` (Python) + `shared/frontend/refs/format.ts` (TS mirror):
  `render_framework_ref(framework, control_id)` e.g.:
  - `EU-73` -> "EU AI Act Art. 73"
  - `NIST-GOVERN-1` -> "NIST AI RMF GOVERN 1"
  - `ISO-4.1` -> "ISO 42001 Clause 4.1"
  - `ISO-A.2` -> "ISO 42001 Annex A.2"
  - `AC.L2-3.1.1` -> "CMMC AC.L2-3.1.1"
  - `CC1.1` -> "SOC 2 CC1.1"
  - `A.5.1` -> "ISO 27001 A.5.1"
- Migrate display consumers to the renderer:
  - `apps/aigovernance/server/tabletop/scenarios.py` frameworkRefs
  - `shared/frontend/gap-analysis/types.ts` clause display
  - `apps/aigovernance/frontend/src/pages/EvidenceRequirementsChecklist.tsx` refs display
  - `apps/aigovernance/core/competence_requirements.py` refs display
  - `apps/aigovernance/frontend/src/pages/ConformityAssessmentPage.tsx` badge
- Fix the `EU.15, NIST.MEASURE.4, ISO.9.1` placeholder in
  `apps/aigovernance/frontend/src/pages/EvaluationsDetailPage.tsx:141` to canonical IDs.
- Unit tests for the Python renderer; `tsc -b` for the TS twin.

## 2. Shared catalog title alignment

- `packages/control_catalog/catalog.py`: ISO 42001 entries (ISO-4.3/4.4/5.2/6.2/8.1/8.3/8.4)
  carry pre-fix buggy titles ("Version Control", "Risk Criteria", ...) -> align to the
  verified aigov catalog titles; align NIST entries (titles + clause strings) too.
- New parity test: overlapping IDs between shared catalog and app catalogs must have
  identical titles.

## 3. Conformity NIST AI RMF rebuild (invented IDs)

- Extract official 22 subcategories (GOVERN 1.1-1.6, MAP 2.1-2.6, MEASURE 3.1-3.4,
  MANAGE 4.1-4.6) from `docs/NIST_AI_RMF_100-1.pdf` (pdftotext, same pattern as
  `apps/cmmc/core/official_800_171.py`).
- Replace the 35 invented articles (MAP 1-15, MEASURE 1-8, MANAGE 1-6, GOVERN 1-6
  refs) in `apps/aigovernance/server/conformity_routes.py` with the official
  subcategories; `control_id` maps to catalog category IDs.
- Fix `apps/aigovernance/tests/test_conformity.py::test_nist_ai_rmf_full_category_coverage`
  (currently asserts MAP=15, MEASURE=8; official: MAP=6, MEASURE=4).
- Verify EU articles against `docs/EU_AI_Act_Regulation_2024_1689.pdf`; fix any
  invented ones.

## 4. Dead `mapped_controls_aigov` mappings

- Remove the `mapped_controls_aigov` field from the 11 templates in
  `packages/policies/templates.py` (they carry 17 nonexistent `AI_*` IDs; each
  template already has real `mapped_controls_eu_ai_act` / `nist_ai_rmf` /
  `iso_42001` mappings).
- Scan test banning `AI_[A-Z]+\.\d` IDs.

## 5. Security fixes

- Bare unauthenticated `fetch()` in `apps/aigovernance/frontend/src/Layout.tsx:42-51`
  and `apps/platform/frontend/src/pages/AiGovPages.tsx` -> route through shared
  `authFetch` convention.
- `apps/soc2/server/auth_middleware.py`: add the sandbox check cmmc/iso have
  (currently silently dropped).
- Unify `/api/collectors/health` in public paths across all 4 framework apps
  (core already has it).
- `apps/soc2/core/app_config.py`: add `INHERITED` to STATUS_OPTIONS (code already
  uses it in priority_queue / my_work).
- Delete confirmed-dead files (`apps/cmmc/frontend/src/pages/Vendors.tsx`,
  platform `AiGovDashboardPage` export — verify imports first).

## 6. Verification

- pytest: aigov suite (conformity + catalog titles + new renderer/parity/scan tests),
  `packages/control_catalog/tests`, cmmc suite.
- `tsc -b` for affected frontends.
- Grep scans: no invented NIST refs (`MAP 1[0-5]`, `MEASURE [5-9]`, `MANAGE [1-6]`
  without 4.), no `AI_[A-Z]+\.\d`, no bare fetch in aigov/platform pages.
