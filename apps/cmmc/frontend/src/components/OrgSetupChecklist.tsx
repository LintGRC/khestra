import { Organization } from "../api";

export type OrgFollowUpItem = {
  id: string;
  label: string;
  detail: string;
  done: boolean;
  optional?: boolean;
  anchor: string;
};

export function orgFollowUpItems(org: Organization): OrgFollowUpItem[] {
  const items: OrgFollowUpItem[] = [];

  if (!org.scope_confirmed) {
    items.push({
      id: "scope",
      label: "Confirm assessment scope",
      detail: "Set CUI Assets % (100% if you handle CUI) and save — this locks which controls apply.",
      done: false,
      anchor: "org-scope",
    });
  }

  if (!org.env_scope_complete) {
    items.push({
      id: "env",
      label: "Complete environment scope",
      detail: "Environment questions tune N/A suggestions and org-aware starter narratives on Controls.",
      done: false,
      anchor: "org-env",
    });
  }

  const hasTopology = Boolean(org.org_assets.topology_filename);
  items.push({
    id: "topology",
    label: "Upload topology diagram",
    detail: "PNG/JPG embeds in SSP export (optional but recommended).",
    done: hasTopology,
    optional: true,
    anchor: "org-topology",
  });

  const hasInventory = (org.org_inventory.assets || []).some((row) =>
    Object.values(row).some((v) => v?.trim()),
  );
  items.push({
    id: "inventory",
    label: "Asset inventory",
    detail: "Import CSV or add rows for appendix references (optional).",
    done: hasInventory,
    optional: true,
    anchor: "org-inventory",
  });

  const coverage = org.scope_coverage;
  items.push({
    id: "coverage",
    label: "Reconcile scope coverage",
    detail: coverage?.has_sync
      ? "Resolve inventory ↔ Intune exceptions in Scope coverage."
      : "Add inventory rows, then run Intune on Integrations.",
    done: Boolean(coverage?.reconciled),
    optional: !coverage?.has_inventory,
    anchor: "org-coverage",
  });

  return items;
}

export function orgFollowUpOpen(items: OrgFollowUpItem[]): boolean {
  return items.some((i) => !i.done && !i.optional);
}

type Props = {
  org: Organization;
};

export default function OrgSetupChecklist({ org }: Props) {
  const items = orgFollowUpItems(org);
  const requiredLeft = items.filter((i) => !i.done && !i.optional);
  const optionalLeft = items.filter((i) => !i.done && i.optional);
  if (requiredLeft.length === 0 && optionalLeft.length === 0) return null;

  const openByDefault = requiredLeft.length > 0;

  return (
    <details className="org-setup-checklist" open={openByDefault}>
      <summary>
        <strong>Complete organization setup</strong>
        <span className="muted">
          {requiredLeft.length > 0
            ? `${requiredLeft.length} required · scroll to sections below`
            : "Optional items remaining"}
        </span>
      </summary>
      <ul>
        {items.map((item) => (
          <li key={item.id} className={item.done ? "done" : item.optional ? "optional" : "required"}>
            <a href={`#${item.anchor}`}>
              {item.done ? "✓ " : item.optional ? "○ " : "• "}
              {item.label}
              {item.optional ? " (optional)" : ""}
            </a>
            {!item.done && <p className="muted">{item.detail}</p>}
          </li>
        ))}
      </ul>
    </details>
  );
}
