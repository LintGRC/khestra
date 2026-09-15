export type AuthConfig = {
  enabled: boolean;
  mode?: string;
  tenant_id: string;
  client_id: string;
  scopes: string[];
  role_locked: boolean;
  login_hint?: string;
};
