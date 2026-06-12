/**
 * KSP Crime Intelligence Platform — API Client
 * Central HTTP client for all backend API calls.
 *
 * Base URL: http://localhost:8000/api/v1
 * Auth: JWT Bearer token
 */

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

// ── Token management ────────────────────────────────────────────────────

let accessToken: string | null = localStorage.getItem("ksp_access_token");
let refreshToken: string | null = localStorage.getItem("ksp_refresh_token");

export function setTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem("ksp_access_token", access);
  localStorage.setItem("ksp_refresh_token", refresh);
}

export function clearTokens() {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem("ksp_access_token");
  localStorage.removeItem("ksp_refresh_token");
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function isAuthenticated(): boolean {
  return !!accessToken;
}

// ── HTTP Client ─────────────────────────────────────────────────────────

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
}

class APIError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public path?: string
  ) {
    super(`API Error ${status}: ${detail}`);
    this.name = "APIError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { body, params, ...init } = options;

  // Build URL with query params
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });
    const qs = searchParams.toString();
    if (qs) url += `?${qs}`;
  }

  // Build headers
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };

  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  const response = await fetch(url, {
    ...init,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  // Handle 401 — try token refresh
  if (response.status === 401 && refreshToken) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${accessToken}`;
      const retry = await fetch(url, {
        ...init,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });
      if (retry.ok) return retry.json();
    }
    clearTokens();
    window.location.reload();
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new APIError(
      response.status,
      errorBody.detail || response.statusText,
      endpoint
    );
  }

  // Handle empty responses
  if (
    response.status === 204 ||
    response.headers.get("content-length") === "0"
  ) {
    return {} as T;
  }

  return response.json();
}

async function tryRefreshToken(): Promise<boolean> {
  try {
    const resp = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (resp.ok) {
      const data = await resp.json();
      setTokens(data.access_token, data.refresh_token);
      return true;
    }
  } catch {}
  return false;
}

// ── Convenience methods ─────────────────────────────────────────────────

export const api = {
  get: <T>(endpoint: string, params?: Record<string, any>) =>
    request<T>(endpoint, { method: "GET", params }),

  post: <T>(endpoint: string, body?: unknown) =>
    request<T>(endpoint, { method: "POST", body }),

  patch: <T>(endpoint: string, body?: unknown) =>
    request<T>(endpoint, { method: "PATCH", body }),

  delete: <T>(endpoint: string) => request<T>(endpoint, { method: "DELETE" }),

  /** Download a file (PDF, CSV) */
  download: async (endpoint: string, filename: string, body?: unknown) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

    const resp = await fetch(url, {
      method: "POST",
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!resp.ok) throw new APIError(resp.status, "Download failed", endpoint);

    const blob = await resp.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  },
};

export { APIError };
export default api;
