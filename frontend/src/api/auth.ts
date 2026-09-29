import { request, setToken, clearToken } from "./client";
import type { User } from "../types";

export async function register(email: string, password: string): Promise<User> {
  return request<User>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

export async function login(email: string, password: string): Promise<string> {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);

  const response = await request<{ access_token: string }>("/api/auth/login", {
    method: "POST",
    body: form
  });

  setToken(response.access_token);
  return response.access_token;
}

export function logout(): void {
  clearToken();
}

export async function fetchMe(): Promise<User> {
  return request<User>("/api/auth/me");
}
