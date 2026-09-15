/** Authenticated JSON fetch for global dashboard pages. */
import { authHeaders } from "@shared/accessToken";

export async function authFetchJson<T = any>(url: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders(init?.headers);
  const r = await fetch(url, { ...init, headers });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(text || `${r.status} ${r.statusText}`);
  }
  return r.json() as Promise<T>;
}
