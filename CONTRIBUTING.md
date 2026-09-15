# Contributing

Thanks for helping improve Khestra. This repository is the open (free) tier:
catalogs, assessment engines, shared GRC tools, and exports. Automated
collector code is **not** part of this repository — do not open PRs adding it.

## Ways to contribute

- **Bug reports** — use the issue template. Include what you expected, what
  happened, and exact steps to reproduce.
- **Catalog accuracy** — control titles, criteria, and points of focus must match
  the official sources. Cite the source in the PR (NIST, AICPA, ISO/IEC, EU).
- **Docs and usability** — clearer setup, better error messages, missing
  coverage of the manual workflow.

## Development

See [Quick start](README.md#quick-start). In short:

```bash
# Backend (per app)
python3 -m venv .venv && . .venv/bin/activate
(cd apps/cmmc && pip install -r requirements.txt)
(cd apps/cmmc && python -m pytest)

# UI
npm ci && cd apps/platform/frontend && npm run dev
```

## Pull request checklist

- [ ] Tests pass for every app you touched (`cd apps/<app> && python -m pytest`)
- [ ] Package tests pass (`cd packages && python -m pytest */tests`)
- [ ] `python tests/leak_check.py` passes (no collector check-ids, no secrets,
      catalogs intact)
- [ ] UI changes build (`npm ci && cd apps/platform/frontend && npx tsc -b && npx vite build`)
- [ ] README/docs updated when behavior or setup changes

Keep pull requests focused on one change; explain the *why* in the description.

## Security

Do not open public issues for vulnerabilities — see [SECURITY.md](SECURITY.md).

## License

By contributing you agree your changes are licensed under Apache-2.0.
