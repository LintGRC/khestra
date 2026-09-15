import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard, Shield, Activity, AlertTriangle,
  FileText, Building2, Database, CheckCircle2, Target,
  BarChart3, Play, Loader2, CheckCircle,
} from "lucide-react";
import type { FrameworkId } from "../framework/frameworks";
import { authHeaders } from "@shared/accessToken";

type FrameworkScore = {
  id: FrameworkId;
  label: string;
  shortLabel: string;
  accentColor: string;
  scores: Record<string, string | number>;
  loading: boolean;
  link: string;
};

type SharedStats = {
  total_risks: number;
  total_findings: number;
  total_assets: number;
  total_tests: number;
  total_audit_entries: number;
};

const PREFIXES: Record<FrameworkId, string> = {
  cmmc: "/api/cmmc",
  soc2: "/api/soc2",
  aigovernance: "/api/ai-governance",
  iso27001: "/api/iso27001",
};

function fmt(n: number): string {
  return n.toLocaleString();
}

function frameworkPrefix(): string {
  const m = location.pathname.match(/^\/(cmmc|soc2|aigov|iso27001)/);
  return m ? m[1] : "";
}

export default function UnifiedDashboard() {
  const loc = useLocation();
  const isRoot = loc.pathname === "/";
  const fwPrefix = frameworkPrefix();
  const [cmmcScore, setCmmcScore] = useState<Record<string, string | number> | null>(null);
  const [soc2Score, setSoc2Score] = useState<Record<string, string | number> | null>(null);
  const [aigovScore, setAigovScore] = useState<Record<string, string | number> | null>(null);
  const [isoScore, setIsoScore] = useState<Record<string, string | number> | null>(null);
  const [sharedStats, setSharedStats] = useState<SharedStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const headersThen = (url: string) =>
      authHeaders().then((headers) => fetch(url, { headers }).then((r) => r.json()));

    const cmmcDash = headersThen(`${PREFIXES.cmmc}/dashboard`).catch(() => null);
    const soc2Dash = headersThen(`${PREFIXES.soc2}/dashboard`).catch(() => null);
    const aigovGov = headersThen(`${PREFIXES.aigovernance}/governance`).catch(() => null);
    const isoDash = headersThen(`${PREFIXES.iso27001}/dashboard`).catch(() => null);

    const allStats = async () => {
      const results = await Promise.allSettled(
        (["cmmc", "soc2", "aigovernance"] as const).flatMap((prefix) => [
          headersThen(`${PREFIXES[prefix]}/risks/stats`),
          headersThen(`${PREFIXES[prefix]}/findings/stats`),
          headersThen(`${PREFIXES[prefix]}/assets/stats`),
          headersThen(`${PREFIXES[prefix]}/testing/stats`),
          headersThen(`${PREFIXES[prefix]}/audit`),
        ]),
      );
      return results as any[];
    };

    Promise.all([cmmcDash, soc2Dash, aigovGov, isoDash, allStats()])
      .then(([cmmc, soc2, aigov, iso, results]) => {
        if (cmmc) setCmmcScore(cmmc);
        if (soc2) setSoc2Score(soc2);
        if (aigov) setAigovScore(aigov);
        if (iso) setIsoScore(iso);

        const totals: SharedStats = { total_risks: 0, total_findings: 0, total_assets: 0, total_tests: 0, total_audit_entries: 0 };
        for (let i = 0; i < 3; i++) {
          const base = i * 5;
          const get = (idx: number) => (results[idx]?.status === "fulfilled" ? results[idx].value as any : null);
          const riskStats = get(base);
          const findingStats = get(base + 1);
          const assetStats = get(base + 2);
          const testStats = get(base + 3);
          const auditData = get(base + 4);

          if (riskStats?.total) totals.total_risks += riskStats.total;
          if (riskStats?.by_status) totals.total_risks += Object.values(riskStats.by_status as Record<string, number>).reduce((a, b) => a + b, 0);
          if (findingStats?.by_status) totals.total_findings += Object.values(findingStats.by_status as Record<string, number>).reduce((a, b) => a + b, 0);
          if (assetStats?.total) totals.total_assets += assetStats.total;
          if (testStats?.total) totals.total_tests += testStats.total;
          if (auditData?.entries?.length) totals.total_audit_entries += auditData.entries.length;
        }
        setSharedStats(totals);
      })
      .finally(() => setLoading(false));
  }, []);

  const frameworks: FrameworkScore[] = [
    {
      id: "cmmc", label: "CMMC Level 2", shortLabel: "CMMC",
      accentColor: "var(--primary)",
      scores: cmmcScore ?? {}, loading: loading && !cmmcScore,
      link: "/cmmc",
    },
    {
      id: "soc2", label: "SOC 2 Type II", shortLabel: "SOC 2",
      accentColor: "var(--info)",
      scores: soc2Score ?? {}, loading: loading && !soc2Score,
      link: "/soc2",
    },
    {
      id: "aigovernance", label: "AI Governance", shortLabel: "AI Gov",
      accentColor: "var(--success)",
      scores: aigovScore ?? {}, loading: loading && !aigovScore,
      link: "/aigov",
    },
    {
      id: "iso27001", label: "ISO 27001", shortLabel: "ISO 27001",
      accentColor: "var(--warning)",
      scores: isoScore ?? {}, loading: loading && !isoScore,
      link: "/iso27001",
    },
  ];

  if (loading && !cmmcScore && !soc2Score && !aigovScore && !isoScore) {
    return <div className="panel" style={{ padding: "3rem 2rem", textAlign: "center", color: "var(--muted)" }}>Loading dashboard…</div>;
  }

  return (
    <div style={{ maxWidth: 1200, margin: "0 auto" }}>
      <div style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: "0 0 0.25rem", display: "flex", alignItems: "center", gap: 8 }}>
          <LayoutDashboard size={22} /> GRC Platform Overview
        </h1>
        <p className="muted" style={{ margin: 0, fontSize: 13 }}>Cross-framework compliance posture at a glance</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16, marginBottom: "1.5rem" }}>
        {frameworks.map((fw) => (
          <NavLink
            key={fw.id}
            to={fw.link}
            className="panel"
            style={{ padding: "1.25rem", textDecoration: "none", color: "inherit", display: "block", borderTop: `3px solid ${fw.accentColor}` }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, margin: 0, color: fw.accentColor }}>{fw.shortLabel}</h3>
              <Shield size={16} style={{ color: fw.accentColor }} />
            </div>
            {fw.loading ? (
              <p className="muted" style={{ fontSize: 12 }}>Loading…</p>
            ) : (
              renderFrameworkScore(fw)
            )}
          </NavLink>
        ))}
      </div>

      <div className="panel" style={{ padding: "1.25rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          <BarChart3 size={16} />
          <strong style={{ fontSize: 14 }}>Shared Package Totals (All Frameworks)</strong>
        </div>
        {sharedStats ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 16 }}>
            <SharedStatCard icon={Activity} label="Risks" value={fmt(sharedStats.total_risks)} color="var(--danger)" />
            <SharedStatCard icon={AlertTriangle} label="Findings" value={fmt(sharedStats.total_findings)} color="var(--warning)" />
            <SharedStatCard icon={Database} label="Assets" value={fmt(sharedStats.total_assets)} color="var(--info)" />
            <SharedStatCard icon={CheckCircle2} label="Control Tests" value={fmt(sharedStats.total_tests)} color="var(--success)" />
            <SharedStatCard icon={FileText} label="Audit Entries" value={fmt(sharedStats.total_audit_entries)} color="var(--primary)" />
          </div>
        ) : (
          <p className="muted" style={{ fontSize: 12 }}>No shared package data yet.</p>
        )}
      </div>

      {isRoot && <DemoProfileSeeding />}

      {!isRoot && (
        <div style={{ marginTop: "1.5rem", display: "flex", gap: 12, flexWrap: "wrap" }}>
          <QuickLink to={"/" + fwPrefix + "/dashboard"} icon={LayoutDashboard} label="My Framework Dashboard" />
          {fwPrefix === "aigov" ? (
            <QuickLink to={"/aigov/systems"} icon={Building2} label="AI Systems" />
          ) : (
            <QuickLink to={"/" + fwPrefix + "/organization"} icon={Building2} label="Organization" />
          )}
          {fwPrefix === "aigov" ? (
            <QuickLink to={"/aigov/dashboard"} icon={Target} label="Compliance Overview" />
          ) : (
            <QuickLink to={"/" + fwPrefix + "/controls"} icon={Target} label="Controls" />
          )}
        </div>
      )}
    </div>
  );
}

type SeedStatus = { label: string; fw?: string; done: boolean; error?: string; skipped?: boolean };

const FW_META: Record<string, { color: string; label: string; api: string }> = {
  cmmc: { color: "#059669", label: "CMMC", api: "/api/cmmc" },
  soc2: { color: "#2563eb", label: "SOC 2", api: "/api/soc2" },
  aigov: { color: "#7c3aed", label: "AI Gov", api: "/api/ai-governance" },
};

async function post(api: string) {
  const headers = await authHeaders();
  const r = await fetch(api, { method: "POST", headers });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json().catch(() => ({}));
}

async function postJson(api: string, body: any) {
  const headers = await authHeaders({ "Content-Type": "application/json" });
  const r = await fetch(api, { method: "POST", headers, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json().catch(() => ({}));
}

async function checkApi(api: string): Promise<boolean> {
  try {
    const r = await fetch(api + "/health", { signal: AbortSignal.timeout(4000) });
    return r.ok;
  } catch {
    return false;
  }
}

function policyDoc(sections: { heading: string; body: string[] }[]): string {
  return JSON.stringify({
    type: "doc",
    content: sections.flatMap((s) => [
      { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: s.heading }] },
      ...s.body.map((text) => ({ type: "paragraph", content: [{ type: "text", text }] })),
    ]),
  });
}

const SAMPLE_POLICIES = [
  {
    title: "Access Control Policy", name: "Access Control Policy",
    description: "Access control and identity management for Trident Defense Systems personnel and systems.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy establishes access control requirements for all Trident Defense Systems information systems and data. It applies to all employees, contractors, and third-party users who access company resources."] },
      { heading: "Scope", body: ["This policy covers all information systems, networks, and data owned or operated by Trident Defense Systems, including cloud services, on-premise infrastructure, and remote access."] },
      { heading: "Policy Requirements", body: ["All users must have a unique user ID for system access.", "Multi-factor authentication (MFA) is required for all administrative and remote access.", "Access reviews must be conducted quarterly for all privileged accounts.", "Account lockout occurs after 5 failed login attempts for 30 minutes.", "Inactive accounts are disabled after 90 days and removed after 180 days."] },
      { heading: "Roles and Responsibilities", body: ["System owners are responsible for granting and revoking access to their systems.", "IT administrators must implement technical controls to enforce access policies.", "Users must protect their credentials and report suspected compromises immediately.", "HR must notify IT within 24 hours of employee termination or role change."] },
      { heading: "Enforcement", body: ["Compliance with this policy is mandatory. Violations may result in disciplinary action up to and including termination of employment or legal action."] },
    ]),
  },
  {
    title: "Incident Response Policy", name: "Incident Response Policy",
    description: "Procedures for detecting, responding to, and recovering from security incidents.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["The purpose of this policy is to establish a standardized approach for responding to security incidents affecting Trident Defense Systems. Effective incident response minimizes impact, preserves evidence, and supports recovery."] },
      { heading: "Incident Classification", body: ["Level 1 — Low: Unauthorized access attempts, minor policy violations. Respond within 24 hours.", "Level 2 — Medium: Successful malware infection, phishing with credentials compromised. Respond within 4 hours.", "Level 3 — High: Data breach affecting classified information, ransomware, system compromise. Respond immediately."] },
      { heading: "Response Phases", body: ["Preparation: Maintain incident response tools, run quarterly tabletop exercises.", "Detection and Analysis: Monitor SIEM alerts, user reports, and automated scanning tools.", "Containment, Eradication, and Recovery: Isolate affected systems, remove threats, restore from verified backups.", "Post-Incident Activity: Conduct root cause analysis, update playbooks, report to relevant authorities within regulatory timelines."] },
      { heading: "Reporting", body: ["All suspected incidents must be reported to the Security Operations Center immediately.", "Regulatory notifications must be completed within applicable timeframes (72 hours for GDPR, 48 hours for CMMC non-compliance events)."] },
      { heading: "Retention", body: ["Incident records must be retained for a minimum of 3 years or as required by applicable regulations."] },
    ]),
  },
  {
    title: "Data Protection Policy", name: "Data Protection Policy",
    description: "Data classification, handling, and protection requirements for Trident Defense Systems.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy defines the data classification framework and handling requirements for all data created, processed, or stored by Trident Defense Systems."] },
      { heading: "Data Classification Levels", body: ["Public: Unclassified information that can be freely distributed. Examples include marketing materials and public job postings.", "Internal: Business information not approved for public release. Examples include internal policies and organizational charts.", "Confidential: Sensitive business information. Examples include customer data, financial records, and strategic plans.", "Restricted: Highly sensitive information subject to regulatory control. Examples include CUI (Controlled Unclassified Information), PII, and classified defense data."] },
      { heading: "Handling Requirements", body: ["Restricted data must be encrypted at rest (AES-256) and in transit (TLS 1.2+).", "Confidential data must be encrypted in transit.", "All data must be classified by the data owner at the time of creation.", "Data minimization principles apply: collect and retain only what is necessary.", "Data disposal must follow NIST SP 800-88 guidelines for media sanitization."] },
      { heading: "Data Retention", body: ["Data retention periods are defined by the data owner based on legal, regulatory, and business requirements.", "Data must be securely deleted at the end of its retention period.", "Retention schedules are reviewed annually."] },
      { heading: "Audit and Compliance", body: ["Compliance with this policy is verified through quarterly access reviews and annual internal audits.", "Data protection controls are tested as part of the continuous monitoring program."] },
    ]),
  },
  {
    title: "Risk Management Policy", name: "Risk Management Policy",
    description: "Enterprise risk management framework for identifying, assessing, and mitigating risks.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy establishes the enterprise risk management (ERM) framework for Trident Defense Systems. It defines the methodology for identifying, assessing, treating, and monitoring risks across the organization."] },
      { heading: "Risk Assessment Methodology", body: ["Risk assessments are conducted using the NIST SP 800-30 methodology.", "Risks are evaluated based on likelihood and impact, scored on a scale of 1-5.", "The risk score is calculated as Likelihood × Impact, with scores ranging from 1 to 25.", "Risk tolerance thresholds: Low (1-6), Moderate (7-14), High (15-25)."] },
      { heading: "Risk Treatment Options", body: ["Avoid: Eliminate the risk by discontinuing the activity.", "Mitigate: Implement controls to reduce likelihood or impact.", "Transfer: Share the risk through insurance or contracts.", "Accept: Formally accept the risk with management sign-off for residual risks below the tolerance threshold."] },
      { heading: "Review Cycle", body: ["Enterprise-level risk assessments are conducted annually.", "System-level risk assessments are conducted during significant changes and at least annually.", "Risk registers are reviewed quarterly by the Risk Management Committee."] },
    ]),
  },
  {
    title: "Business Continuity Policy", name: "Business Continuity Policy",
    description: "Business continuity and disaster recovery planning for Trident Defense Systems.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy establishes the framework for business continuity management and disaster recovery at Trident Defense Systems. The goal is to ensure critical business functions can continue during and after a disruptive event."] },
      { heading: "Scope", body: ["This policy covers all critical business functions, information systems, facilities, and personnel at Trident Defense Systems."] },
      { heading: "Business Impact Analysis", body: ["A business impact analysis (BIA) must be conducted annually to identify critical functions and their recovery priorities.", "Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO) are defined for each critical system.", "Minimum RTO for mission-critical systems: 4 hours. Maximum RPO: 1 hour."] },
      { heading: "Plan Requirements", body: ["Business Continuity Plans (BCP) and Disaster Recovery Plans (DRP) must be documented, tested, and maintained for all critical functions.", "Plans must be reviewed and updated at least annually or after any major change.", "Tabletop exercises are conducted quarterly; full functional exercises are conducted annually."] },
      { heading: "Testing and Maintenance", body: ["BCP/DRP tests must be documented with findings and corrective actions tracked to closure.", "Alternate processing sites must be tested at least annually.", "All employees must complete continuity awareness training upon hire and annually thereafter."] },
    ]),
  },
  {
    title: "Backup and Recovery Policy", name: "Backup and Recovery Policy",
    description: "Backup frequency, retention, and recovery testing for Trident Defense Systems systems.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy defines backup and recovery requirements for information systems that store or process Trident Defense Systems data, including CUI."] },
      { heading: "Backup Requirements", body: ["Critical systems are backed up daily; full backups run weekly.", "Backup integrity is verified after each full backup cycle.", "Backups containing CUI must be encrypted at rest."] },
      { heading: "Retention", body: ["Online/incremental backups are retained for 30 days.", "Weekly full backups are retained for 90 days.", "Quarterly archive backups are retained for 1 year unless legal hold requires longer."] },
      { heading: "Recovery Testing", body: ["Recovery procedures are tested at least quarterly for mission-critical systems.", "Test results and corrective actions are documented in the recovery log."] },
    ]),
  },
  {
    title: "Physical and Environmental Security Policy", name: "Physical and Environmental Security Policy",
    description: "Physical access and environmental controls for facilities hosting Trident systems.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy establishes physical and environmental security requirements for facilities that store, process, or transmit organizational information."] },
      { heading: "Physical Access", body: ["Access to server rooms and wiring closets is restricted to authorized personnel.", "Visitor access requires escort and logging.", "Badge access is reviewed quarterly."] },
      { heading: "Environmental Controls", body: ["Data center spaces maintain temperature and humidity within manufacturer guidelines.", "Fire detection/suppression and UPS coverage are required for critical rooms."] },
    ]),
  },
  {
    title: "Identification and Authentication Policy", name: "Identification and Authentication Policy",
    description: "Identity proofing, authentication, and authenticator management requirements.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy defines identification and authentication requirements for users, devices, and services that access Trident Defense Systems information systems."] },
      { heading: "Identification", body: ["Every user is assigned a unique identifier; shared accounts are prohibited except for approved break-glass procedures.", "Device and service identities are enrolled before production use."] },
      { heading: "Authentication", body: ["MFA is required for privileged, remote, and CUI system access.", "Authenticator secrets meet organizational complexity and rotation requirements.", "Failed authentication attempts are logged and monitored."] },
    ]),
  },
  {
    title: "Vendor Management Policy", name: "Vendor Management Policy",
    description: "Third-party risk management and vendor oversight for Trident Defense Systems.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy establishes requirements for assessing, contracting, and monitoring vendors that access Trident systems or data."] },
      { heading: "Due Diligence", body: ["Vendors are risk-tiered before onboarding.", "Security questionnaires and SOC 2 / equivalent reports are collected for high-risk vendors."] },
      { heading: "Contracts", body: ["Agreements include security, confidentiality, incident notification, and data return/destruction clauses.", "CUI handling requirements are explicit when applicable."] },
      { heading: "Ongoing Monitoring", body: ["High-risk vendors are reviewed at least annually.", "Material incidents or control regressions trigger an out-of-cycle review."] },
    ]),
  },
  {
    title: "Audit and Accountability Policy", name: "Audit and Accountability Policy",
    description: "Logging, review, and retention requirements for Trident Defense Systems.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy defines audit logging and accountability requirements to support detection, investigation, and compliance."] },
      { heading: "Logging", body: ["Systems that process or store CUI generate auditable events for authentication, privilege use, and access to sensitive data.", "Clocks are synchronized to an authoritative time source."] },
      { heading: "Review", body: ["Security logs are reviewed on a defined cadence commensurate with system risk.", "Automated alerting is configured for privileged activity and failure thresholds."] },
      { heading: "Retention", body: ["Audit records are retained for at least 1 year, or longer when required by contract or regulation."] },
    ]),
  },
  {
    title: "Business Continuity and Disaster Recovery Policy", name: "Business Continuity and Disaster Recovery Policy",
    description: "Expanded BCDR requirements covering failover and communication for major disruptions.",
    version: "1.0",
    content: policyDoc([
      { heading: "Purpose", body: ["This policy complements the Business Continuity Policy with disaster recovery and crisis communication requirements."] },
      { heading: "Failover", body: ["Critical workloads have documented failover runbooks and designated owners.", "Failover contact trees are maintained and tested annually."] },
      { heading: "Communication", body: ["Incident commanders coordinate internal and customer communications during DR events.", "Regulatory and contractual notifications follow approved timelines."] },
    ]),
  },
];

function DemoProfileSeeding() {
  const [seeding, setSeeding] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [statuses, setStatuses] = useState<SeedStatus[]>([]);
  const [done, setDone] = useState(false);
  const [clearDone, setClearDone] = useState(false);

  const clearAll = async () => {
    if (!window.confirm("Clear all demo data from all frameworks? This cannot be undone.")) return;
    setClearing(true);
    setClearDone(false);
    const results: SeedStatus[] = [];
    for (const [fwId, meta] of Object.entries(FW_META)) {
      try {
        await post(`${meta.api}/demo/clear`);
        results.push({ label: "Demo data cleared", fw: fwId, done: true });
      } catch {
        try {
          await post(`${meta.api}/clear`);
          results.push({ label: "Demo data cleared", fw: fwId, done: true });
        } catch {
          results.push({ label: "Clear not available", fw: fwId, done: true, skipped: true });
        }
      }
      setStatuses([...results]);
    }
    setClearing(false);
    setClearDone(true);
  };

  const seedAll = async () => {
    setSeeding(true);
    setDone(false);
    setStatuses([]);

    const results: SeedStatus[] = [];
    const update = () => setStatuses([...results]);

    for (const [fwId, meta] of Object.entries(FW_META)) {
      const add = (label: string, fn: () => Promise<any>) => ({ label, fn });

      const available = await checkApi(meta.api);
      if (!available) {
        results.push({ label: "Backend not running", fw: fwId, done: true, skipped: true });
        update();
        continue;
      }

      const steps: { label: string; fn: () => Promise<any> }[] = [
        add("Demo workspace", () =>
          post(
            `${meta.api}/demo/load?demo_id=${fwId === "cmmc" ? "trident" : "northwind"}&org_name=Trident+Defense+Systems`,
          ),
        ),
      ];

      if (fwId === "aigov") {
        steps.push(add("AI systems", () => post(`${meta.api}/seed`)));
        steps.push(add("FRIAs", () => post(`${meta.api}/frias/seed`)));
        steps.push(add("Vendors", () => post(`${meta.api}/vendor-intake/seed`)));
      }

      steps.push(add("Clear existing sample policies", async () => {
        const headers = await authHeaders();
        const r = await fetch(`${meta.api}/policies`, { headers });
        if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
        const res = await r.json().catch(() => ({ policies: [] }));
        const sampleTitles = new Set(SAMPLE_POLICIES.map((p) => p.title));
        const existing = ((res.policies || []) as any[]).filter((p) => sampleTitles.has(p.title));
        await Promise.all(
          existing.map(async (p: any) => {
            const dr = await fetch(`${meta.api}/policies/${p.id}`, { method: "DELETE", headers: await authHeaders() });
            if (!dr.ok) throw new Error(`${dr.status} ${dr.statusText}`);
          }),
        );
      }));

      steps.push(add("Incidents", () => post(`${meta.api}/incidents/seed`)));
      steps.push(add("Vendors", () => post(`${meta.api}/vendors/seed?force=true`)));
      steps.push(add("Exceptions", () => post(`${meta.api}/exceptions/seed`)));

      for (const p of SAMPLE_POLICIES) {
        const fwKey = fwId === "aigovernance" || fwId === "aigov" ? "aigov" : fwId;
        steps.push(add(`Policy: ${p.title}`, () => postJson(`${meta.api}/policies`, { ...p, mapped_controls: { [fwKey]: ["ACCESS.1", "ACCESS.2"] } })));
      }

      for (const step of steps) {
        try {
          await step.fn();
          results.push({ label: step.label, fw: fwId, done: true });
        } catch (e) {
          results.push({ label: step.label, fw: fwId, done: true, error: String(e) });
        }
        update();
      }
    }

    setSeeding(false);
    setDone(true);
  };

  return (
    <div className="panel" style={{ marginTop: "1.5rem", padding: "1.25rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <Play size={16} />
        <strong style={{ fontSize: 14 }}>Demo Profile — Trident Defense Systems</strong>
      </div>
      <p className="muted" style={{ fontSize: 12, margin: "0 0 12px" }}>
        Seeds a unified company profile across all available frameworks. Frameworks whose backend is not running are skipped.
      </p>
      {statuses.length > 0 && (
        <div style={{ marginBottom: 12, display: "flex", flexDirection: "column", gap: 1, fontSize: 11 }}>
          {statuses.map((s, i) => {
            const meta = s.fw ? FW_META[s.fw] : null;
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 6, padding: "2px 0" }}>
                {s.skipped ? (
                  <span style={{ color: "var(--muted)" }}>–</span>
                ) : seeding && i === statuses.length - 1 ? (
                  <Loader2 size={11} className="spin" />
                ) : s.error ? (
                  <span style={{ color: "var(--warning)" }}>⚠</span>
                ) : (
                  <CheckCircle size={11} style={{ color: "var(--success)" }} />
                )}
                {meta && <span style={{ color: meta.color, fontWeight: 600, width: 48, flexShrink: 0 }}>{meta.label}</span>}
                <span style={{ color: s.skipped ? "var(--muted)" : "inherit" }}>{s.label}</span>
                {s.error && <span className="muted" style={{ fontSize: 10 }}>({s.error})</span>}
              </div>
            );
          })}
        </div>
      )}
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={seedAll}
          disabled={seeding}
          style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
        >
          {seeding ? <Loader2 size={14} className="spin" /> : done ? <CheckCircle size={14} /> : <Play size={14} />}
          {seeding ? `Seeding (${statuses.length})…` : done ? "Demo Loaded" : "Load Demo Data"}
        </button>
        {done && (
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => location.reload()}>
            Reload page
          </button>
        )}
        {!seeding && (done || clearDone || statuses.length > 0) && (
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={clearAll}
            disabled={clearing}
            style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
          >
            {clearing ? `Clearing…` : "Clear Demo Data"}
          </button>
        )}
      </div>
    </div>
  );
}

function renderFrameworkScore(fw: FrameworkScore) {
  const s = fw.scores;
  switch (fw.id) {
    case "cmmc": {
      const sprs = (s as any).sprs_score;
      const max = (s as any).sprs_max || 110;
      const gaps = (s as any).open_gaps;
      const progress = (s as any).controls_assessed != null && (s as any).controls_total
        ? Math.round(((s as any).controls_assessed / (s as any).controls_total) * 100)
        : null;
      return (
        <div>
          <div style={{ fontSize: 24, fontWeight: 700 }}>{sprs != null ? `${sprs}/${max}` : "—"}</div>
          <div className="muted" style={{ fontSize: 11 }}>SPRS Score</div>
          <div style={{ marginTop: 8, display: "flex", gap: 16, fontSize: 12 }}>
            {progress != null && <span><strong>{progress}%</strong> assessed</span>}
            {gaps != null && <span style={{ color: gaps > 0 ? "var(--danger)" : "inherit" }}><strong>{gaps}</strong> open gaps</span>}
          </div>
        </div>
      );
    }
    case "soc2": {
      const readiness = (s as any).readiness_pct;
      const met = (s as any).controls_met;
      const total = (s as any).controls_total;
      const gaps = (s as any).open_gaps;
      return (
        <div>
          <div style={{ fontSize: 24, fontWeight: 700 }}>{readiness != null ? `${readiness}%` : "—"}</div>
          <div className="muted" style={{ fontSize: 11 }}>Readiness</div>
          <div style={{ marginTop: 8, display: "flex", gap: 16, fontSize: 12 }}>
            {met != null && total != null && <span><strong>{met}/{total}</strong> controls met</span>}
            {gaps != null && <span style={{ color: gaps > 0 ? "var(--danger)" : "inherit" }}><strong>{gaps}</strong> gaps</span>}
          </div>
        </div>
      );
    }
    case "aigovernance": {
      const systems = (s as any).total_systems;
      const highRisk = (s as any).high_risk;
      const incidents = (s as any).total_incidents;
      const production = (s as any).production_systems;
      return (
        <div>
          <div style={{ fontSize: 24, fontWeight: 700 }}>{systems != null ? systems : "—"}</div>
          <div className="muted" style={{ fontSize: 11 }}>AI Systems</div>
          <div style={{ marginTop: 8, display: "flex", gap: 16, fontSize: 12 }}>
            {highRisk != null && <span style={{ color: highRisk > 0 ? "var(--danger)" : "inherit" }}><strong>{highRisk}</strong> high risk</span>}
            {production != null && <span><strong>{production}</strong> in production</span>}
            {incidents != null && <span><strong>{incidents}</strong> incidents</span>}
          </div>
        </div>
      );
    }
    case "iso27001": {
      const readiness = (s as any).readiness_pct;
      const counts = (s as any).rollup?.counts;
      const implemented = counts?.implemented;
      const tests = (s as any).tests_total;
      const evidence = (s as any).evidence_total;
      return (
        <div>
          <div style={{ fontSize: 24, fontWeight: 700 }}>{readiness != null ? `${readiness}%` : "—"}</div>
          <div className="muted" style={{ fontSize: 11 }}>Implemented</div>
          <div style={{ marginTop: 8, display: "flex", gap: 16, fontSize: 12 }}>
            {implemented != null && <span><strong>{implemented}</strong> controls</span>}
            {tests != null && <span><strong>{tests}</strong> tests</span>}
            {evidence != null && <span><strong>{evidence}</strong> evidence</span>}
          </div>
        </div>
      );
    }
    default:
      return null;
  }
}

function SharedStatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div style={{ width: 36, height: 36, borderRadius: 8, background: `${color}15`, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Icon size={16} style={{ color }} />
      </div>
      <div>
        <div style={{ fontSize: 18, fontWeight: 700 }}>{value}</div>
        <div className="muted" style={{ fontSize: 11 }}>{label}</div>
      </div>
    </div>
  );
}

function QuickLink({ to, icon: Icon, label }: { to: string; icon: any; label: string }) {
  return (
    <NavLink
      to={to}
      className="btn btn-secondary btn-sm"
      style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, textDecoration: "none" }}
    >
      <Icon size={14} /> {label}
    </NavLink>
  );
}
