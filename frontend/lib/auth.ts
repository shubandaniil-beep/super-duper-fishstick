export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("km_token");
}

export function getUser(): Record<string, string> | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("km_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setAuth(token: string, user: Record<string, string>) {
  localStorage.setItem("km_token", token);
  localStorage.setItem("km_user", JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem("km_token");
  localStorage.removeItem("km_user");
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
