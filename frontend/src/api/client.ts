const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function setToken(token: string): void {
  localStorage.setItem("access_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("access_token");
}

async function extractError(response: Response): Promise<ApiError> {
  let detail = response.statusText;

  try {
    const payload = await response.json();
    detail = typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail);
  } catch {
    detail = response.statusText;
  }

  return new ApiError(response.status, detail);
}

function buildHeaders(options: RequestInit): Headers {
  const headers = new Headers(options.headers);
  const token = getToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const isFormData = options.body instanceof FormData;
  const isUrlSearchParams = options.body instanceof URLSearchParams;

  if (options.body && !isFormData && !isUrlSearchParams) {
    headers.set("Content-Type", "application/json");
  }

  return headers;
}

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: buildHeaders(options)
  });

  if (!response.ok) {
    throw await extractError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function requestBlob(path: string): Promise<Blob> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: buildHeaders({})
  });

  if (!response.ok) {
    throw await extractError(response);
  }

  return response.blob();
}
