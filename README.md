# Khestra

**Self-hosted GRC assessments for CMMC, SOC 2, ISO 27001, and AI governance — manual but complete, with audit-ready deliverables.**

Built by [LintGRC](https://github.com/LintGRC). Apache-2.0.

Khestra is for defense subcontractors, compliance teams, auditors, and MSPs who need a real assessment workspace — not a marketing checklist. Run a CMMC Level 2 self-assessment, attach evidence, compute SPRS, and export an SSP / POA&M without paying for automation. The same workspace covers SOC 2, ISO 27001, and AI governance (NIST AI RMF, EU AI Act curated subset, ISO 42001), plus shared assets, vendors, policies, risks, and an evidence hub.

Open-core model: **catalogs, assessment engines, shared GRC tools, and exports are free.** Automated evidence collectors and hosted operations are paid, and the collector code is not part of this repository.

## What's free vs paid

| Included in this repo (free) | Paid / hosted |
|---|---|
| CMMC, SOC 2, ISO 27001, AI Gov apps | Continuous evidence **collectors** |
| Control catalogs + assessment engines | Hosted fleet (TLS, backups, upgrades) |
| Manual evidence upload, review, mapping | Hosted AI key (BYOK stays free) |
| Shared modules: assets, vendors, policies, risks, personnel, incidents, audit log | Ongoing regulatory content update service |
| Deliverables: SPRS, SSP, POA&M, SoA, system description, auditor exports | Support / SLA |
| Docker Compose self-hosting | |

When collectors are not installed, posture is computed from **approved manual evidence** in the Evidence Hub — the free tier is complete by hand, not a hollow stub.

## Example: CMMC self-assessment

1. Start the stack (`docker compose up --build -d` — see Quick start).
2. Create a workspace / org profile and scope controls.
3. Set control status, write implementation narratives, upload evidence.
4. Review SPRS score and gaps.
5. Export SSP (DOCX), POA&M (XLSX), and related packages.

No collectors required for that loop — that is the free tier by design.

## Scope & limitations

Stated up front on purpose:

- **SOC 2** — Prepares you for Type I and Type II audits. Type II readiness depends on real period-covered evidence; we do not claim Type II compliance out of the box.
- **EU AI Act** — Covers a curated subset of ~40 high-relevance obligations, not the full regulation.
- **Not a certification** — Khestra prepares you for audits and assessments. It does not certify or accredit; certification rests with your assessor / C3PAO.
- **CMMC Level 3** and some federal/GovCloud connector variants are out of scope for this release.

## Prerequisites

- **Docker** + Docker Compose (recommended), **or**
- **Python 3.12+** and **Node.js 20+** for local development
- A machine with enough RAM for several API + frontend processes (local) or the Compose fleet (production-shaped)

## Quick start

**Compose (production-shaped):**

```bash
cp deploy/env.production.example .env   # set DOMAIN and a strong admin password
docker compose up --build -d
```

Caddy terminates TLS for `DOMAIN`; all five APIs and the UI come up behind it. Volumes persist the shared auth DB, evidence hub, and framework data between restarts.

**Local development (per app, Python 3.12+):**

`security_headers` is installed as an editable dependency, and pip resolves such
paths relative to the current directory — so install from the app directory:

```bash
python3 -m venv .venv && . .venv/bin/activate
(cd apps/cmmc && pip install -r requirements.txt)
uvicorn main:app --app-dir apps/cmmc/server --host 127.0.0.1 --port 8081 --reload
```

Swap `cmmc` for `soc2` (8082), `aigovernance` (8083), `iso27001` (8085), or
`core` (8086) to run the other services.

**Local development (unified UI):**

Install UI dependencies at the **repo root** (mirrors `Dockerfile.caddy`, so
TypeScript/Vite can resolve modules from `shared/` and each app's frontend):

```bash
npm ci
cd apps/platform/frontend && npm run dev   # http://127.0.0.1:5173
```

The dev server proxies `/api/*` to the services above.

**Backups, restore, and upgrades (Compose):**

The `shared_auth` volume holds the auth database, the Evidence Hub, and every
framework's data. Back it up regularly (the volume is named
`<compose-project>_shared_auth`; the project defaults to the checkout directory
name — `khestra` below):

```bash
docker run --rm \
  -v khestra_shared_auth:/data \
  -v "$PWD/backups:/backup" \
  alpine tar czf "/backup/shared_auth-$(date +%Y%m%d-%H%M%S).tgz" -C /data .
```

Restore by stopping the stack, unpacking the archive back into the volume, and
starting again. (`scripts/backup.sh` does the same for non-Docker data dirs.)

Upgrade with `git pull`, then `docker compose build --pull && docker compose up -d`.
Database files are created or backfilled on startup.

**Security:** see [`SECURITY.md`](SECURITY.md). Authentication is enabled by
`CMMC_AUTH_MODE=local` (or Entra ID); the API is unauthenticated if it is unset.
Baseline login rate limiting is built in (`AUTH_RATE_LIMIT_*` env vars); add
proxy-level limits for public internet exposure.

**Tests:**

```bash
pip install pytest httpx
cd apps/cmmc && python -m pytest
```

Run the suites from each `apps/<framework>/` directory. The `packages/` tree includes its own tests.

## Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system design and routing
- [`docs/ACCURACY_BACKLOG.md`](docs/ACCURACY_BACKLOG.md) — framework content verification
- [`docs/CROSS_FRAMEWORK_CONSIDERATIONS.md`](docs/CROSS_FRAMEWORK_CONSIDERATIONS.md) — framework overlap notes
- [`docs/STYLE_CONSISTENCY_PLAN.md`](docs/STYLE_CONSISTENCY_PLAN.md) — UI consistency plan
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) — attribution for incorporated standards

## Help & contributing

- **Bugs and questions:** open an issue on this repository.
- **Security reports:** prefer a private channel to the LintGRC maintainers rather than a public issue with exploit detail.
- Pull requests that improve docs, catalog accuracy, or free-tier usability are welcome. Automated collector code is **not** part of this repository.

## License

Khestra is licensed under the Apache License 2.0. See [`LICENSE`](LICENSE) for the full text and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for attribution of incorporated standards and third-party content.
