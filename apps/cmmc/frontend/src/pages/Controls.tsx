import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import { api, ControlSummary, FamilyFilterOption, NextAssessment } from "../api";
import { useLayout } from "../Layout";
import AssessmentInsightsPanel from "../components/AssessmentInsightsPanel";
import ContinueAssessmentHero from "../components/ContinueAssessmentHero";
import ControlCard from "../components/ControlCard";
import ControlsPriorityQueue from "../components/ControlsPriorityQueue";
import ControlsPrefillPanel from "../components/ControlsPrefillPanel";
import ControlsMyWorkPanel from "../components/ControlsMyWorkPanel";
import SspProgressStrip from "../components/SspProgressStrip";
import PageIntro from "../components/PageIntro";
import SprsWeightBadge, { focusAnchorId } from "../components/SprsWeightBadge";
import ControlsFamilyScrollLabel from "../components/ControlsFamilyScrollLabel";
import { familyScrollLabel, groupControlsByFamily } from "../lib/groupControlsByFamily";
import { FilterSearch, FilterSelect } from "@shared/filter-bar";

type BrowseMode = "table" | "cards";
type PageMode = "queue" | "browse";

const BROWSE_MODE_KEY = "controlsBrowseLayout";

const PAGE_SIZES = [5, 10, 15, 25] as const;

function readPageSize(): number {
  const n = Number(localStorage.getItem("controlsPageSize"));
  return (PAGE_SIZES as readonly number[]).includes(n) ? n : 15;
}

function readBrowseMode(): BrowseMode {
  return localStorage.getItem(BROWSE_MODE_KEY) === "table" ? "table" : "cards";
}

function statusClass(status: string) {
  if (status === "MET" || status === "NOT APPLICABLE" || status === "INHERITED") return "met";
  if (status === "NOT MET" || status === "NOT STARTED") return "gap";
  return "neutral";
}

export default function ControlsPage() {
  const { canEdit, refreshDashboard, settings, openWorkspace } = useLayout();
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "/cmmc";
  const navigate = useNavigate();
  const isExecutive = settings?.current_role === "Executive";
  const [searchParams, setSearchParams] = useSearchParams();
  const focusId = searchParams.get("focus") || "";
  const [family, setFamily] = useState("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(0);
  const [controls, setControls] = useState<ControlSummary[]>([]);
  const [familyOptions, setFamilyOptions] = useState<FamilyFilterOption[]>([]);
  const [statusOptions, setStatusOptions] = useState<string[]>([]);
  const [next, setNext] = useState<NextAssessment | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [pageSize, setPageSize] = useState(readPageSize);
  const [pageMode, setPageMode] = useState<PageMode>("browse");
  const [browseMode, setBrowseMode] = useState<BrowseMode>(readBrowseMode);
  const scrolledFocus = useRef("");

  const [assignedOnly, setAssignedOnly] = useState(false);
  const [missingSspOnly, setMissingSspOnly] = useState(false);

  const reload = () =>
    api.controls(family || undefined, q || undefined, assignedOnly ? "me" : undefined).then((data) => {
      setControls(data.controls);
      setFamilyOptions(data.family_options || []);
      setStatusOptions(data.status_options);
    });

  useEffect(() => {
    setPage(0);
    reload().catch(console.error);
  }, [family, q, assignedOnly]);

  useEffect(() => {
    api.nextControl().then(setNext).catch(console.error);
  }, [controls.length]);

  useEffect(() => {
    localStorage.setItem("controlsPageMode", pageMode);
  }, [pageMode]);

  useEffect(() => {
    localStorage.setItem(BROWSE_MODE_KEY, browseMode);
  }, [browseMode]);

  useEffect(() => {
    localStorage.setItem("controlsPageSize", String(pageSize));
    setPage(0);
  }, [pageSize]);

  useEffect(() => {
    if (pageMode !== "browse" || !focusId || scrolledFocus.current === focusId) return;
    const anchor = focusAnchorId(focusId);
    const el = document.getElementById(anchor);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      scrolledFocus.current = focusId;
    }
  }, [focusId, page, pageMode, browseMode, controls.length]);

  useEffect(() => {
    if (focusId) {
      setPageMode("browse");
    }
  }, [focusId]);

  const goToFocus = (controlId: string) => {
    setPageMode("browse");
    setSearchParams({ focus: controlId });
    scrolledFocus.current = "";
    const idx = controls.findIndex((c) => c.id === controlId);
    if (idx >= 0) {
      setPage(Math.floor(idx / pageSize));
    }
  };

  const onStatusChange = async (id: string, status: string) => {
    setSavingId(id);
    try {
      await api.patchControl(id, { status });
      await refreshDashboard();
      await reload();
      api.nextControl().then(setNext).catch(console.error);
    } finally {
      setSavingId(null);
    }
  };

  const pageCount = Math.max(1, Math.ceil(controls.length / pageSize));
  const filteredControls = useMemo(() => {
    if (!missingSspOnly) return controls;
    return controls.filter((c) => !c.has_narrative);
  }, [controls, missingSspOnly]);

  const pageCountFiltered = Math.max(1, Math.ceil(filteredControls.length / pageSize));
  const visible = useMemo(() => {
    const source = pageMode === "browse" && missingSspOnly ? filteredControls : controls;
    const slice = source.slice(page * pageSize, (page + 1) * pageSize);
    if (!focusId || !slice.some((c) => c.id === focusId)) return slice;
    const focused = slice.find((c) => c.id === focusId)!;
    return [focused, ...slice.filter((c) => c.id !== focusId)];
  }, [controls, filteredControls, page, pageSize, focusId, pageMode, missingSspOnly]);

  const familyMeta = useMemo(() => {
    const map = new Map<string, FamilyFilterOption>();
    familyOptions.forEach((opt) => map.set(opt.family, opt));
    return map;
  }, [familyOptions]);

  const visibleFamilyGroups = useMemo(() => groupControlsByFamily(visible), [visible]);
  const showFamilyLabels = visibleFamilyGroups.length > 0;
  const tableColSpan = assignedOnly ? 6 : 5;

  const priorityRows = next?.priority_details?.length
    ? next.priority_details
    : (next?.priority_controls || []).map((id) => ({ id, name: "", family: "", status: "", weight_tier: "standard", weight_badge: "" }));

  return (
    <>
      <PageIntro view="Controls" />
      <ContinueAssessmentHero
        next={next}
        onContinue={(id) => {
          navigate(`${fwBase}/controls/${encodeURIComponent(id)}`)
        }}
      />
      <SspProgressStrip
        missingFilterActive={missingSspOnly}
        onShowMissing={() => {
          setMissingSspOnly((v) => !v);
          setPageMode("browse");
          setPage(0);
        }}
      />
      <AssessmentInsightsPanel priorityRows={priorityRows} onGoToControl={goToFocus} />

      {pageMode === "queue" && (
        <ControlsMyWorkPanel
          onBrowseAssigned={() => {
            setAssignedOnly(true);
            setPageMode("browse");
            setPage(0);
            reload().catch(console.error);
          }}
          onSetUserName={openWorkspace}
        />
      )}

      {pageMode === "queue" && (
        <ControlsPrefillPanel
          canEdit={canEdit}
          onApplied={() => {
            refreshDashboard().catch(console.error);
            reload().catch(console.error);
            api.nextControl().then(setNext).catch(console.error);
          }}
        />
      )}

      {pageMode === "queue" ? (
        <ControlsPriorityQueue
          rows={priorityRows}
          onBrowseAll={() => setPageMode("browse")}
        />
      ) : (
        <>
          <div className="controls-browse-bar">
            <button type="button" className="btn-link" onClick={() => { setAssignedOnly(false); setPageMode("queue"); }}>
              ← Priority queue
            </button>
            {settings?.current_user_name && (
              <label className="controls-assigned-filter">
                <input
                  type="checkbox"
                  checked={assignedOnly}
                  onChange={(e) => {
                    setAssignedOnly(e.target.checked);
                    setPage(0);
                  }}
                />
                Assigned to me ({settings.current_user_name})
              </label>
            )}
          </div>

          <div className="filters controls-toolbar">
            <div className="controls-toolbar-filters">
              <FilterSearch value={q} onChange={setQ} placeholder="Search controls…" />
              <FilterSelect value={family} onChange={setFamily} options={familyOptions.map((f) => ({ value: f.family, label: f.label }))} placeholder="All families" />
            </div>
            <div className="controls-toolbar-options">
              <div className="view-toggle" role="group" aria-label="View mode">
                <button
                  type="button"
                  className={browseMode === "cards" ? "active" : ""}
                  onClick={() => setBrowseMode("cards")}
                >
                  Cards
                </button>
                <button
                  type="button"
                  className={browseMode === "table" ? "active" : ""}
                  onClick={() => setBrowseMode("table")}
                >
                  Table
                </button>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <strong>
                {missingSspOnly ? `${filteredControls.length} controls missing SSP text` : `${controls.length} controls`}
              </strong>
            </div>

            {browseMode === "cards" ? (
              <div className="panel-body control-card-grid">
                {showFamilyLabels
                  ? visibleFamilyGroups.map((group) => (
                      <section key={group.family} className="controls-family-section" aria-label={group.family}>
                        <ControlsFamilyScrollLabel
                          {...familyScrollLabel(group.controls, group.family, familyMeta.get(group.family)?.code)}
                        />
                        {group.controls.map((c) => (
                          <ControlCard
                            key={c.id}
                            control={c}
                            focused={focusId === c.id}
                            canEdit={canEdit}
                            executiveView={isExecutive}
                            statusOptions={statusOptions}
                            saving={savingId === c.id}
                            onStatusChange={onStatusChange}
                          />
                        ))}
                      </section>
                    ))
                  : visible.map((c) => (
                      <ControlCard
                        key={c.id}
                        control={c}
                        focused={focusId === c.id}
                        canEdit={canEdit}
                        executiveView={isExecutive}
                        statusOptions={statusOptions}
                        saving={savingId === c.id}
                        onStatusChange={onStatusChange}
                      />
                    ))}
              </div>
            ) : (
              <div className="panel-body data-table-wrap" style={{ padding: 0 }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Control</th>
                      <th>Status</th>
                      {assignedOnly && <th>Owner</th>}
                      <th>Weight</th>
                      <th>Narrative</th>
                      <th>Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {showFamilyLabels
                      ? visibleFamilyGroups.map((group) => (
                          <Fragment key={group.family}>
                            <tr className="controls-family-label-row">
                              <td colSpan={tableColSpan}>
                                <ControlsFamilyScrollLabel
                                  {...familyScrollLabel(group.controls, group.family, familyMeta.get(group.family)?.code)}
                                />
                              </td>
                            </tr>
                            {group.controls.map((c) => (
                              <tr key={c.id} id={focusAnchorId(c.id)} className={focusId === c.id ? "row-focused" : ""}>
                                <td>
                                  <Link to={`${encodeURIComponent(c.id)}`}>
                                    <strong className="control-id-text">{c.id}</strong>
                                  </Link>
                                  <div className="muted control-requirement-text" title={c.name}>{c.name}</div>
                                </td>
                                <td>
                                  {canEdit ? (
                                    <select
                                      className="inline-status"
                                      value={c.status}
                                      disabled={savingId === c.id}
                                      onChange={(e) => onStatusChange(c.id, e.target.value)}
                                    >
                                      {statusOptions.map((s) => (
                                        <option key={s} value={s}>{s}</option>
                                      ))}
                                    </select>
                                  ) : (
                                    <span className={`badge ${statusClass(c.status)}`}>{c.status}</span>
                                  )}
                                </td>
                                {assignedOnly && <td>{c.owner || "—"}</td>}
                                <td>
                                  <SprsWeightBadge
                                    label={c.weight_badge || `${c.weight} PT`}
                                    tier={c.weight_tier || "standard"}
                                  />
                                </td>
                                <td>{c.has_narrative ? "Yes" : "—"}</td>
                                <td>{c.evidence_count || "—"}</td>
                              </tr>
                            ))}
                          </Fragment>
                        ))
                      : visible.map((c) => (
                          <tr key={c.id} id={focusAnchorId(c.id)} className={focusId === c.id ? "row-focused" : ""}>
                            <td>
                              <Link to={`${encodeURIComponent(c.id)}`}>
                                <strong className="control-id-text">{c.id}</strong>
                              </Link>
                              <div className="muted control-requirement-text" title={c.name}>{c.name}</div>
                            </td>
                            <td>
                              {canEdit ? (
                                <select
                                  className="inline-status"
                                  value={c.status}
                                  disabled={savingId === c.id}
                                  onChange={(e) => onStatusChange(c.id, e.target.value)}
                                >
                                  {statusOptions.map((s) => (
                                    <option key={s} value={s}>{s}</option>
                                  ))}
                                </select>
                              ) : (
                                <span className={`badge ${statusClass(c.status)}`}>{c.status}</span>
                              )}
                            </td>
                            {assignedOnly && <td>{c.owner || "—"}</td>}
                            <td>
                              <SprsWeightBadge
                                label={c.weight_badge || `${c.weight} PT`}
                                tier={c.weight_tier || "standard"}
                              />
                            </td>
                            <td>{c.has_narrative ? "Yes" : "—"}</td>
                            <td>{c.evidence_count || "—"}</td>
                          </tr>
                        ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="panel-footer pagination">
              <div className="pagination-meta">
                {(missingSspOnly ? pageCountFiltered : pageCount) > 1 && (
                  <span className="muted">
                    Page {page + 1} of {missingSspOnly ? pageCountFiltered : pageCount}
                  </span>
                )}
                <label className="panel-page-size">
                  <select
                    value={pageSize}
                    onChange={(e) => setPageSize(Number(e.target.value))}
                    aria-label="Controls per page"
                  >
                    {PAGE_SIZES.map((n) => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                  <span className="muted">rows</span>
                </label>
              </div>
              {(missingSspOnly ? pageCountFiltered : pageCount) > 1 && (
                <div className="pagination-nav">
                  <button type="button" className="btn-secondary" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
                    Previous
                  </button>
                  <button
                    type="button"
                    className="btn-secondary"
                    disabled={page >= (missingSspOnly ? pageCountFiltered : pageCount) - 1}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Next
                  </button>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </>
  );
}
