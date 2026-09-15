"""Help and FAQ content — no Streamlit."""

VIEW_HELP = {
    "Dashboard": {
        "title": "Dashboard",
        "summary": "SPRS score, journey progress, and what to do next.",
        "tips": [
            "Fix **5-point gaps** first — biggest impact on SPRS.",
            "Use **Continue assessment** on Controls for the next priority item.",
            "Load **Apex demo** from the sidebar to explore a filled workspace.",
        ],
    },
    "Organization": {
        "title": "Organization",
        "summary": "Company and system info — flows into your SSP export.",
        "tips": [
            "Use **Guided setup** for step-by-step first profile.",
            "Set **CUI Assets** to 100% if you handle CUI, then save scope.",
            "Upload topology PNG and appendix files for a fuller SSP.",
            "Import asset inventory CSV or edit the table directly.",
        ],
    },
    "Controls": {
        "title": "Controls",
        "summary": "Review each control: status, narrative, evidence, POA&M fields.",
        "tips": [
            "Open **Guidance** on each control for catalog text and starter narrative.",
            "MET controls need an **SSP description** before export.",
            "Upload evidence on controls — filenames are listed at the bottom of that control in the SSP export; files are in the **audit package** zip.",
        ],
    },
    "Readiness": {
        "title": "Readiness",
        "summary": "Checklist and package before a C3PAO conversation.",
        "tips": [
            "Self-ready is heuristic — fix 5-point gaps regardless of score.",
            "Review **readiness findings** before scheduling assessor.",
            "SPRS Entry Summary is for manual PIEE entry — no API.",
        ],
    },
    "Export": {
        "title": "Export",
        "summary": "Generate SSP, POA&M, and audit packages from current data.",
        "tips": [
            "Check **export stale** warning — rebuild SSP after assessment changes.",
            "SSP **references** evidence by filename; the **audit package** zip contains the actual files.",
            "Download **audit package** for C3PAO prep.",
            "Use **family SSP** export for partial reviews.",
        ],
    },
    "Integrations": {
        "title": "Integrations",
        "summary": "Connect cloud and dev tools to collect evidence snapshots for mapped controls.",
        "tips": [
            "Use **Demo (fixture)** to test collectors without live credentials.",
            "Collectors attach JSON evidence — they do **not** auto-set MET or NOT MET.",
            "Enable **daily/weekly** schedules; production uses `workers/run_due.py` or cron on **Run due**.",
            "Review drift and freshness before an assessor visit — stale evidence may need a re-run.",
        ],
    },
}

FAQ = [
    {
        "q": "Where is my data saved?",
        "a": "Under cmmc_data/ in this install — organization profile, control answers, evidence files, and connector credentials. In the default local setup, everything stays on the machine running the API.",
    },
    {
        "q": "What order should I work in?",
        "a": "Follow the sidebar: **Organization** (profile, scope, inventory) → **Controls** (status, SSP narrative, evidence) → **Readiness** (gaps before an assessor) → **Export** (SSP, POA&M, audit package). **Integrations** can run anytime to attach collector snapshots.",
    },
    {
        "q": "Do integrations auto-pass controls?",
        "a": "No. Entra, AWS, GitHub, and Intune collectors attach JSON evidence to mapped controls. You still set MET / NOT MET and write narratives. Collectors do not change SPRS by themselves.",
    },
    {
        "q": "Does exported Word sync back here?",
        "a": "No. Edit controls here and re-export when something changes. POA&M CSV import can pull spreadsheet updates back into control records.",
    },
    {
        "q": "Does this submit to SPRS or eMASS?",
        "a": "No. Copy **SPRS Entry Summary** from Readiness into PIEE manually when your organization is ready.",
    },
    {
        "q": "How do I explore without live cloud credentials?",
        "a": "Workspace → load the **Apex demo**, or on Integrations use **Try demo (fixture)** per connector. Fixtures use bundled sample JSON — safe for pilots and walkthroughs.",
    },
    {
        "q": "What is scope coverage on Organization?",
        "a": "A thin check between your declared asset inventory and Intune device snapshots — flags undeclared, unmanaged, or stale items. Reconciliation aid only, not full asset-management software.",
    },
]
