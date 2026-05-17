import { request } from "@/utils/request";

export interface UserInfo {
  id: number;
  username: string | null;
  openid: string | null;
  display_name: string;
  role: "super_admin" | "sub_admin" | "counselor" | "visitor";
  email: string | null;
  avatar_url: string | null;
  bio: string | null;
  specialties: string | null;
  status: "active" | "disabled" | "deleted";
  must_change_password: boolean;
  sub_admin_permissions: string | null;
  created_at: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
  must_change_password?: boolean;
}

export interface AdminLoginParams {
  username: string;
  password: string;
}

export interface ChangePasswordParams {
  old_password?: string;
  new_password: string;
}

export interface ForgotPasswordParams {
  email: string;
}

export interface ResetPasswordParams {
  token: string;
  new_password: string;
}

export function wechatLogin(data: {
  openid: string;
  display_name: string;
  avatar_url?: string;
}): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/wechat-login", { method: "POST", data });
}

export function adminLogin(data: AdminLoginParams): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/admin-login", { method: "POST", data });
}

export function getCurrentUser(): Promise<UserInfo> {
  return request<UserInfo>("/api/auth/me");
}

export function changePassword(data: ChangePasswordParams): Promise<any> {
  return request("/api/auth/change-password", { method: "POST", data });
}

export function forgotPassword(data: ForgotPasswordParams): Promise<any> {
  return request("/api/auth/forgot-password", { method: "POST", data });
}

export function resetPassword(data: ResetPasswordParams): Promise<any> {
  return request("/api/auth/reset-password", { method: "POST", data });
}