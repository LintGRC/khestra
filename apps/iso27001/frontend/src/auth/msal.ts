import {
  Configuration,
  LogLevel,
  PublicClientApplication,
} from "@azure/msal-browser";
import type { AuthConfig } from "./types";

export function buildMsalConfig(config: AuthConfig): Configuration {
  return {
    auth: {
      clientId: config.client_id,
      authority: `https://login.microsoftonline.com/${config.tenant_id}`,
      redirectUri: window.location.origin,
      postLogoutRedirectUri: window.location.origin,
    },
    cache: {
      cacheLocation: "sessionStorage",
    },
    system: {
      loggerOptions: {
        logLevel: LogLevel.Warning,
      },
    },
  };
}

export function createMsalInstance(config: AuthConfig): PublicClientApplication {
  return new PublicClientApplication(buildMsalConfig(config));
}

export async function acquireApiToken(
  instance: PublicClientApplication,
  scopes: string[],
  loginHint?: string,
): Promise<string | null> {
  const account = instance.getActiveAccount() ?? instance.getAllAccounts()[0];
  if (!account) {
    return null;
  }
  try {
    const result = await instance.acquireTokenSilent({ account, scopes });
    return result.accessToken;
  } catch {
    const result = await instance.acquireTokenPopup({
      account,
      scopes,
      loginHint: loginHint || undefined,
    });
    return result.accessToken;
  }
}
