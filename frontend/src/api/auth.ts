import { request } from "@/utils/request";

export interface UserInfo {
  id: number;
  username: string;
  display_name: string;
  role: "admin" | "counselor" | "visitor";
  phone: string | null;
  is_active: boolean;
}

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  password: string;
  display_name: string;
  role: string;
  phone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export function login(params: LoginParams): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/login", {
    method: "POST",
    data: params,
  });
}

export function register(params: RegisterParams): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/register", {
    method: "POST",
    data: params,
  });
}

export function getCurrentUser(): Promise<UserInfo> {
  return request<UserInfo>("/api/auth/me");
}