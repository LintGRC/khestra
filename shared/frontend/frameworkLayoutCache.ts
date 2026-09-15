/** Prefetched layout bootstrap data for fast framework switches on unified platform. */

export type LayoutBootstrapCache = {
  dashboard: unknown;
  settings: unknown;
  demoStatus: unknown;
  journey?: unknown;
  fetchedAt: number;
};

const cache = new Map<string, LayoutBootstrapCache>();
const inflight = new Map<string, Promise<LayoutBootstrapCache | null>>();

const TTL_MS = 60_000;

function isFresh(entry: LayoutBootstrapCache): boolean {
  return Date.now() - entry.fetchedAt < TTL_MS;
}

export function peekLayoutCache(apiPrefix: string): LayoutBootstrapCache | null {
  const entry = cache.get(apiPrefix);
  return entry && isFresh(entry) ? entry : null;
}

export function clearLayoutCache(apiPrefix?: string) {
  if (apiPrefix) cache.delete(apiPrefix);
  else cache.clear();
}

/** Fetch dashboard, settings, and demo status for a framework API prefix. */
export async function prefetchLayoutData(
  apiPrefix: string,
  opts?: { includeJourney?: boolean },
): Promise<LayoutBootstrapCache | null> {
  const existing = peekLayoutCache(apiPrefix);
  if (existing) return existing;

  const pending = inflight.get(apiPrefix);
  if (pending) return pending;

  const work = (async () => {
    const base = apiPrefix.replace(/\/$/, "");
    const get = async (path: string) => {
      const res = await fetch(`${base}${path}`);
      if (!res.ok) throw new Error(`${path}: ${res.status}`);
      return res.json();
    };

    try {
      const [dashboard, settings, demoStatus] = await Promise.all([
        get("/dashboard"),
        get("/settings"),
        get("/demo/status"),
      ]);
      let journey: unknown;
      if (opts?.includeJourney) {
        try {
          journey = await get("/journey");
        } catch {
          /* CMMC-only; ignore on SOC 2 */
        }
      }
      const entry: LayoutBootstrapCache = {
        dashboard,
        settings,
        demoStatus,
        journey,
        fetchedAt: Date.now(),
      };
      cache.set(apiPrefix, entry);
      return entry;
    } catch {
      return null;
    } finally {
      inflight.delete(apiPrefix);
    }
  })();

  inflight.set(apiPrefix, work);
  return work;
}
