/** JSON fetch with optional timeout — avoids infinite loading when API is hung. */

const DEFAULT_TIMEOUT_MS = 20_000;

export async function fetchJson<T>(
  url: string,
  init?: RequestInit,
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...init, signal: controller.signal });
    if (res.status === 401) {
      localStorage.removeItem("khestra_auth_token");
      window.location.href = window.location.pathname.substring(0, window.location.pathname.indexOf("/app")) || "/";
      throw new Error("Session expired — redirecting to login");
    }
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || res.statusText);
    }
    return res.json() as Promise<T>;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error(`Request timed out after ${Math.round(timeoutMs / 1000)}s — API may be hung. Restart ./run-dev.sh.`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}
