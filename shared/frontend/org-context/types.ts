export interface InterestedParty {
  name: string;
  requirements: string[];
  addressed_via_isms: boolean;
  notes?: string;
}

export type ClimateStatus = "not_assessed" | "relevant" | "not_relevant";

export interface ContextRecord {
  id: string;
  label: string;
  internal_issues: string[];
  external_issues: string[];
  interested_parties: InterestedParty[];
  climate_relevant: boolean;
  climate_note: string;
  climate_status: ClimateStatus;
  scope_statement: string;
  boundaries: string;
  interfaces_dependencies: string[];
  created_at: string;
  updated_at: string;
}

export interface ContextCreateBody {
  label?: string;
  internal_issues?: string[];
  external_issues?: string[];
  interested_parties?: InterestedParty[];
  climate_relevant?: boolean;
  climate_note?: string;
  climate_status?: ClimateStatus;
  scope_statement?: string;
  boundaries?: string;
  interfaces_dependencies?: string[];
}
