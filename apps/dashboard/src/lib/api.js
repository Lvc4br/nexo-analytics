const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

let accessToken = null;

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, init = {}) {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  let response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, { ...init, headers });
  } catch {
    throw new ApiError("Não foi possível acessar a API Python. Confira se o backend está iniciado.", 0);
  }

  if (response.status === 204) return undefined;
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) accessToken = null;
    throw new ApiError(payload.detail || "A API não conseguiu concluir a solicitação.", response.status);
  }
  return payload;
}

export async function login(email, password) {
  const result = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  accessToken = result.access_token;
}

export function logout() {
  accessToken = null;
}

export function hasSession() {
  return accessToken !== null;
}

export function getOverview(days) {
  return request(`/analytics/overview?days=${days}`);
}
