import { createContext, useContext } from "react";

export type AuthContextValue = {
  ready: boolean;
  enabled: boolean;
  authenticated: boolean;
  displayName: string;
  email: string;
  role: string;
  login: (email?: string, password?: string) => Promise<void>;
  logout: () => Promise<void>;
};

export const defaultAuthContext: AuthContextValue = {
  ready: false,
  enabled: false,
  authenticated: false,
  displayName: "",
  email: "",
  role: "",
  login: async () => {},
  logout: async () => {},
};

export const AuthContext = createContext<AuthContextValue>(defaultAuthContext);

export function useAuth() {
  return useContext(AuthContext);
}
