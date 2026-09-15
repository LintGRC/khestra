/** Shared bearer token getter for unified platform (CMMC + SOC 2 APIs). */

let accessTokenGetter: (() => Promise<string | null>) | null = null;

export function setAccessTokenGetter(getter: (() => Promise<string | null>) | null) {
  accessTokenGetter = getter;
}

export async function authHeaders(init?: HeadersInit): Promise<Headers> {
  const headers = new Headers(init);
  if (accessTokenGetter) {
    const token = await accessTokenGetter();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }
  return headers;
}
