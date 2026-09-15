# Khestra

Multi-framework GRC platform for CMMC, SOC 2, and AI Governance.

---

## Role-Based Access Control (RBAC)

### Authentication Roles — Route-Level Access

Roles defined in `packages/auth/store.py`:

| Role | Manage Users (invite/create/patch/delete) | Change Org Admin | View Self |
|------|:-:|:-:|:-:|
| **Organization Admin** | ✅ | ✅ | ✅ |
| **Compliance Manager** | ✅ | ❌ | ✅ |
| **Assessor** | ❌ | ❌ | ✅ |
| **Engineer** | ❌ | ❌ | ✅ |
| **Executive** | ❌ | ❌ | ✅ |
| **Auditor** | ❌ | ❌ | ✅ |

- `_require_admin()` — Allowed: **Organization Admin**, **Compliance Manager**
- `_require_org_admin()` — Allowed: **Organization Admin** only

---

### CMMC App Permissions

Defined in `apps/cmmc/core/app_config.py`:

| Permission | Org Admin | Compliance Manager | Assessor | Engineer | Executive | Auditor |
|---|---|---|---|---|---|---|
| View Dashboard | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Edit Controls | ✅ | ✅ | ✅ | ✅ | — | — |
| Validate Evidence | ✅ | ✅ | ✅ | ✅ | — | — |
| Approve POA&M | ✅ | ✅ | — | — | ✅ | ✅ |
| Export Data | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Manage Users | ✅ | ✅ | — | — | — | — |
| Manage Billing | ✅ | — | — | — | — | — |

**Key:**
- **Organization Admin** — Full access, can manage org, billing, and users
- **Compliance Manager** — Full data access, can manage users, no billing
- **Assessor** — Full data access, no user management
- **Engineer** — Edit controls and validate evidence only, no dashboard
- **Executive** — Read + approve POA&M + export, no editing
- **Auditor** — Read + export only

---

### SOC2 App Permissions

Defined in `apps/soc2/core/app_config.py`:

| Permission | Assessor | Engineer | Executive |
|---|---|---|---|
| View Dashboard | ✅ | ✅ | ✅ |
| Edit Controls | ✅ | ✅ | — |

---

### Org-Level Roles (Multi-Tenant)

Defined in `packages/orgs/models.py`:

| Permission | Owner | Admin | Member | Viewer |
|---|---|---|---|---|
| Manage Org | ✅ | — | — | — |
| Manage Members | ✅ | ✅ | — | — |
| Edit Controls | ✅ | ✅ | ✅ | — |
| View All | ✅ | ✅ | — | ✅ |
| Export | ✅ | ✅ | — | — |

---

### Recommended Role for Demo Users

For a demo account that can **view and write** but **not manage users**:

> **"Assessor"** — Can view dashboard, edit controls, validate evidence, export data. Cannot manage users or billing.

