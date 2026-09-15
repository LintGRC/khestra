import type { Organization } from "../api";

type Props = {
  org: Organization;
};

type CheckItem = {
  key: string;
  label: string;
  required: boolean;
  href: string;
};

function orgFollowUpItems(org: Organization): CheckItem[] {
  const items: CheckItem[] = [];
  const profile = org.org_profile || {};

  if (!profile.org_name || profile.org_name === "Your Organization") {
    items.push({ key: "identity", label: "Set organization name", required: true, href: "#org-identity" });
  }
  if (!profile.system_description) {
    items.push({ key: "description", label: "Add system description", required: true, href: "#org-description" });
  }
  if (!profile.system_owner) {
    items.push({ key: "owner", label: "Assign system owner", required: true, href: "#org-roles" });
  }
  if (!org.env_scope_complete) {
    items.push({ key: "env", label: "Complete environment scope", required: true, href: "#org-env" });
  }
  if (!(org.org_inventory?.assets || []).length) {
    items.push({ key: "inventory", label: "Add asset inventory", required: false, href: "#org-inventory" });
  }

  return items;
}

function orgFollowUpOpen(items: CheckItem[]): boolean {
  return items.some((i) => i.required);
}

export default function OrgSetupChecklist({ org }: Props) {
  const items = orgFollowUpItems(org);
  if (!items.length) return null;
  const isOpen = orgFollowUpOpen(items);

  return (
    <details className="panel" open={isOpen} style={{ marginBottom: 16 }}>
      <summary style={{ cursor: "pointer", fontWeight: 600, padding: "12px 16px" }}>
        Setup checklist ({items.filter((i) => i.required).length} required remaining)
      </summary>
      <div style={{ padding: "0 16px 12px" }}>
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {items.map((item) => (
            <li key={item.key} style={{ padding: "6px 0" }}>
              <a
                href={item.href}
                className="btn-link"
                style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: 8 }}
              >
                <span
                  className={`badge ${item.required ? "badge-warning" : "badge-muted"}`}
                  style={{ fontSize: 10, minWidth: 20, textAlign: "center" }}
                >
                  {item.required ? "!" : "~"}
                </span>
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </details>
  );
}
