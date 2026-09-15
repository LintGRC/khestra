export type AssetItem = {
  id: string;
  name: string;
  type: string;
  owner: string;
  description: string;
  environment: string;
  data_classification: string;
  handles_cui: boolean;
  location: string;
  criticality: string;
  framework_tags: string[];
  org_id: string;
  workspace_id: string;
  created_at: string;
  updated_at: string;
};
