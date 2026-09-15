# Third-Party Notices

Khestra incorporates summaries, references, and mappings from publicly available
standards and frameworks. This document describes the licensing and attribution
status of that content.

## Standards and frameworks

### NIST SP 800-171, NIST SP 800-171A, NIST SP 800-172

Source: U.S. National Institute of Standards and Technology (NIST)

Status: Public domain; works of the U.S. federal government are not subject to
copyright. NIST publications may be freely redistributed.

Usage in Khestra: CMMC control text, assessment objectives, and security
requirement mappings are derived from NIST publications.

### NIST AI Risk Management Framework (AI RMF) 1.0

Source: U.S. National Institute of Standards and Technology (NIST)

Status: Public domain; freely redistributable.

Usage in Khestra: AI governance functions and categories are based on the NIST
AI RMF.

### EU AI Act (Regulation (EU) 2024/1689)

Source: European Union

Status: Public law; legal texts are not subject to copyright and may be freely
redistributed.

Usage in Khestra: EU AI Act articles and obligations are referenced in the AI
governance module.

### SOC 2 Trust Services Criteria (TSC) 2017

Source: American Institute of Certified Public Accountants (AICPA)

Status: Copyrighted by AICPA. Khestra stores criterion identifiers and
faithful paraphrases of the official titles and points of focus; it does not
redistribute the full AICPA standard text.

Usage in Khestra: SOC 2 criterion statements, points of focus, and DC Section 200
paraphrases are derived from the official AICPA text and cross-checked against
a local reference copy. Paraphrases are used in the open-source catalog to
respect AICPA copyright.

### ISO/IEC 27001:2022, ISO/IEC 27002:2022, ISO/IEC 27005:2022

Source: International Organization for Standardization (ISO) / International
Electrotechnical Commission (IEC)

Status: Copyrighted by ISO/IEC. Khestra stores clause identifiers and
summaries; it does not redistribute the full standard text.

Usage in Khestra: ISO 27001 clauses, Annex A controls, and risk assessment
references are derived from ISO/IEC standards.

### ISO/IEC 42001:2023

Source: International Organization for Standardization (ISO) / International
Electrotechnical Commission (IEC)

Status: Copyrighted by ISO/IEC. Khestra stores clause identifiers and
summaries; it does not redistribute the full standard text.

Usage in Khestra: AI management system clauses and Annex A categories are
derived from ISO/IEC 42001.

### CIS Benchmarks

Source: Center for Internet Security (CIS)

Status: Copyrighted by CIS. Khestra references CIS benchmarks by name and does
not redistribute benchmark content.

Usage in Khestra: Collector checks may reference CIS benchmarks as a source of
evidence mapping.

## Software dependencies

Khestra depends on many open-source Python and Node.js packages. License
texts for those packages are included in the installed dependencies and are not
reproduced here. To produce a full dependency license report, run:

```bash
pip install pip-licenses
pip-licenses --format=markdown
```

for Python packages, and consult `package-lock.json` for Node.js packages.

## Trademarks

All trademarks, service marks, and product names mentioned above are the
property of their respective owners. Use of these names in Khestra is for
identification and reference only and does not imply endorsement.
