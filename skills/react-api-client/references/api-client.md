# Reference — ApiClient + error normalization + auth store (production-extracted, condensed)

## errors.ts — typed taxonomy

```ts
export enum ErrorCodes {
  INSUFFICIENT_BALANCE = 'INSUFFICIENT_BALANCE',
  COOLDOWN_ACTIVE = 'COOLDOWN_ACTIVE',
  TARGET_OFFLINE = 'TARGET_OFFLINE',
  LIMIT_REACHED = 'LIMIT_REACHED',
  NOT_PERMITTED = 'NOT_PERMITTED',    // 403 — authenticated, not allowed; NEVER logs out
  ACTION_DISABLED = 'ACTION_DISABLED',
  UNAUTHORIZED = 'UNAUTHORIZED',      // 401 refresh could not recover
  NETWORK = 'NETWORK',                // no response: timeout/offline
  UNKNOWN = 'UNKNOWN',
}

export class ApiException extends Error {
  readonly code: ErrorCodes;
  readonly status?: number;
  readonly raw?: unknown;             // raw backend payload — feature code may read raw.code
  readonly details?: { fields?: Record<string, string>; meta?: Record<string, unknown> };
  // constructor({ code, message, status?, raw?, details? }) ...
}
export const isApiException = (e: unknown): e is ApiException => e instanceof ApiException;
```

## client.ts — the interceptor contract (essence)

```ts
export interface AuthHandlers {
  getAccessToken: () => string | null;
  onUnauthorized: () => void;
  refresh?: () => Promise<string | null>;   // absent ⇒ 401 logs out immediately
}

export class ApiClient {
  private handlers: AuthHandlers | null = null;
  private refreshInFlight: Promise<string | null> | null = null;

  setAuthHandlers(h: AuthHandlers) { this.handlers = h; }   // breaks api⇄auth cycle

  // request interceptor: inject `Authorization: Bearer <token>` unless cfg.skipAuth

  private async handleResponseError(error: unknown): Promise<never> {
    if (!(error instanceof AxiosError) || !error.response) throw normalizeError(error);
    const status = error.response.status;
    const original = error.config as RetriableConfig | undefined;

    if (status === 403) throw normalizeError(error);          // forbidden ≠ logged out

    if (status === 401 && original && !original._retried && !original.skipAuth) {
      const newToken = await this.runRefresh();               // single-flight
      if (newToken) {
        original._retried = true;                             // retry exactly once
        original.headers.set('Authorization', `Bearer ${newToken}`);
        try { return (await this.instance.request(original)) as never; }
        catch (retryError) { throw normalizeError(retryError); }
      }
      this.handlers?.onUnauthorized();                        // session dead
      throw new ApiException({ code: ErrorCodes.UNAUTHORIZED, status, message: 'Session expired.' });
    }
    if (status === 401) { this.handlers?.onUnauthorized(); /* throw UNAUTHORIZED */ }
    throw normalizeError(error);
  }

  /** Concurrent 401s await the SAME refresh promise — no stampede. */
  private runRefresh(): Promise<string | null> {
    if (!this.handlers?.refresh) return Promise.resolve(null);
    if (!this.refreshInFlight) {
      this.refreshInFlight = this.handlers.refresh()
        .catch(() => null)
        .finally(() => { this.refreshInFlight = null; });
    }
    return this.refreshInFlight;
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await this.instance.get<T>(url, config);
    return res.data;                                          // envelope NOT unwrapped here
  }
  // post/put/patch/delete<T> identical
}

export const createApiClient = (cfg: ApiClientConfig) => new ApiClient(cfg);
```

## normalize.ts — one funnel

- No response → `NETWORK` (distinct timeout vs offline messages).
- Response with known body `code` → that code; else `401→UNAUTHORIZED`, `403→NOT_PERMITTED`;
  else `UNKNOWN`. Extracts `message`/`detail`, `fields`, `meta`; keeps `raw`.
- Idempotent: an `ApiException` passes through unchanged.

## createAuthStore.ts — factory essentials

```ts
export function createAuthStore({ persistKey }: { persistKey: string }) {
  return createStore(persist(
    (set) => ({
      tokens: null, user: null, isAuthenticated: false,
      setSession: (tokens, user) => set({ tokens, user, isAuthenticated: true }),
      clear: () => set({ tokens: null, user: null, isAuthenticated: false }),
    }),
    {
      name: persistKey,
      storage: createSafeStorage(),          // probe with a real write; fallback: in-memory Map
      partialize: (s) => ({ tokens: s.tokens }),  // ONLY tokens persist — user re-derived at boot
    },
  ));
}
```

Boot gate (per app): tokens-but-no-user → `GET /auth/me` → `setSession`, else `clear()`;
`cancelled` flag guards the StrictMode double-mount.

## Dedup nonce for paid mutations

```ts
const dedupKey = typeof crypto !== 'undefined' && crypto.randomUUID
  ? crypto.randomUUID()
  : `${Date.now()}-${Math.random().toString(36).slice(2)}`;  // non-secure context (LAN/IP)
await api.post('/interactions/trigger', { target_id, action_type, dedup_key: dedupKey });
```
