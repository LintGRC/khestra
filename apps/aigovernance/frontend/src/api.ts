import { apiUrl } from "@shared/apiPrefix";
import { authHeaders, setAccessTokenGetter } from "@shared/accessToken";

export { apiUrl };
export { setAccessTokenGetter };

export async function authFetch(url: string, init?: RequestInit): Promise<Response> {
  const headers = await authHeaders(init?.headers);
  if (!headers.has("Content-Type") && init?.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(apiUrl(url), { ...init, headers });
  if (res.status === 401) {
    localStorage.removeItem("khestra_auth_token");
    window.location.href = window.location.pathname.substring(0, window.location.pathname.indexOf("/app")) || "/";
    throw new Error("Session expired — redirecting to login");
  }
  return res;
}

const json = async <T>(url: string, init?: RequestInit): Promise<T> => {
  const headers = await authHeaders(init?.headers);
  if (!headers.has("Content-Type") && init?.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(apiUrl(url), { ...init, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
};

export const api = {
  help: () => json<{ views: Record<string, { title: string; summary: string; tips: string[] }>; faq: { q: string; a: string }[] }>("/api/help"),
};

export async function postDownload(url: string, init?: RequestInit, filename?: string): Promise<void> {
  const headers = await authHeaders(init?.headers);
  if (!headers.has("Content-Type") && init?.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(apiUrl(url), { ...init, method: "POST", headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const disposition = res.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^";]+)"?/);
  const blob = await res.blob();
  const objectUrl = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = objectUrl;
  a.download = filename || match?.[1] || "download";
  a.click();
  URL.revokeObjectURL(objectUrl);
}
