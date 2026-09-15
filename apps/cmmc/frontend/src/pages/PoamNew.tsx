import { useSearchParams } from "react-router-dom";
import ExceptionCreate from "@shared/exception-tracker/pages/ExceptionCreate";

const LIKELIHOOD_MAP: Record<string, number> = {
  critical: 5, high: 4, medium: 3, low: 2, info: 1,
};

export default function PoamNew() {
  const [params] = useSearchParams();

  const initialForm = params.has("finding_title")
    ? {
        title: params.get("finding_title") ?? "",
        description: params.get("finding_description") ?? "",
        control_id: params.get("finding_control_id") ?? "",
        control_reference: params.get("finding_control_id") ?? "",
        framework: params.get("finding_framework") ?? "CMMC",
        owner: params.get("finding_owner") ?? "",
        likelihood: LIKELIHOOD_MAP[params.get("finding_severity") ?? ""] ?? 3,
        impact: LIKELIHOOD_MAP[params.get("finding_severity") ?? ""] ?? 3,
      }
    : undefined;

  return <ExceptionCreate title="POA&M" basePath="/poam" initialForm={initialForm} />;
}
