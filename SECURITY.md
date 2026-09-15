# Security Policy

Khestra is compliance infrastructure: please report suspected vulnerabilities
privately, not in a public issue.

## Supported versions

Khestra is pre-1.0. Security fixes land on the `main` branch; run the latest
commit or release tag.

## Reporting a vulnerability

Use **GitHub private vulnerability reporting** on this repository
(*Security → Report a vulnerability*), or email **security@lintgrc.com**.

Please include:

- affected component and version/commit,
- reproduction steps or a proof of concept,
- impact assessment (what an attacker gains),
- any suggested remediation.

We aim to acknowledge reports within 3 business days, keep you updated while we
investigate, and coordinate disclosure timing with you.

## Scope

**In scope:** code in this repository — the five framework apps, shared
packages, container images, Compose files, and the documented self-host path.

**Out of scope:** findings requiring a compromised host or network position,
social engineering, volumetric denial-of-service, and third-party dependency
issues without a demonstrated impact on Khestra (report those upstream).

## Hardening notes for self-hosters

- **Enable authentication.** Set `CMMC_AUTH_MODE=local` (or Entra). If unset,
  the API runs without authentication.
- **TLS + network exposure.** The bundled Caddy terminates TLS for `DOMAIN`.
  For public exposure, put the stack behind a VPN or IP allowlist, or configure
  Entra ID, and enable the production auth-posture guard
  (`KHESTRA_ENV=production`, `KHESTRA_TRUSTED_NETWORK=1` for local auth).
- **Baseline rate limiting** is built in for `/auth/login` (see
  `AUTH_RATE_LIMIT_*` env vars). Add proxy-level limits for internet exposure.
- **Secrets.** Keep `CMMC_ADMIN_PASSWORD`, `CMMC_AUTH_SECRET`, and connector
  credentials out of the repository and rotate anything that was ever exposed.
- **Backups.** Back up the `shared_auth` volume (see README) — it holds the
  auth database, evidence hub, and all framework data.
