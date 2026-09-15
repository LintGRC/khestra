## Summary

<!-- What changed and why -->

## Checklist

- [ ] Tests pass for every app touched (`cd apps/<app> && python -m pytest`)
- [ ] Package tests pass (`cd packages && python -m pytest */tests`)
- [ ] `python tests/leak_check.py` passes
- [ ] UI builds if frontend changed (`npm ci && cd apps/platform/frontend && npx tsc -b && npx vite build`)
- [ ] Docs updated when setup or behavior changed
